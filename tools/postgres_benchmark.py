#!/usr/bin/env python3
"""Run one governed ARGUS PostgreSQL concurrency benchmark scenario.

The connection string is accepted only through ``ARGUS_BENCHMARK_DSN`` so a
credential cannot be placed in the process list. Every reader transaction is
read-only. Writer probes touch deterministic synthetic rows and roll back every
update; enabling them requires an explicit command-line acknowledgement.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import queue
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence


SEARCH_SQL = (
    "SELECT canonical_tender_id, tender_reference, project_code, title, "
    "buyer_name, status, closing_at, source_url, score "
    "FROM argus.search_tenders(%s, %s, 20)"
)
LIST_SQL = (
    "SELECT canonical_tender_id, tender_reference, project_code, title, "
    "buyer_name, status, closing_at, source_url "
    "FROM argus.list_tenders('published', NULL, 20)"
)
READ_QUERIES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("exact_reference", SEARCH_SQL, ("exact_reference", "REF-000001")),
    ("exact_project_code", SEARCH_SQL, ("exact_project_code", "PRJ-000001")),
    ("fts", SEARCH_SQL, ("fts", "marine communications")),
    ("fuzzy", SEARCH_SQL, ("fuzzy", "Marine comunications equipmnt")),
    ("active_closing_date", LIST_SQL, ()),
)
WRITE_SQL = (
    "UPDATE argus.tender "
    "SET attributes = jsonb_set("
    "attributes, '{benchmark_probe}', to_jsonb(clock_timestamp()::text), true"
    ") WHERE canonical_tender_id = %s"
)

Sample = tuple[str, float, int, str | None]


def percentile(values: Sequence[float], fraction: float) -> float | None:
    """Return a nearest-rank percentile rounded to microsecond precision."""
    if not values:
        return None
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be greater than zero and at most one")
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return round(ordered[index], 3)


def summarize_samples(samples: Sequence[Sample]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[tuple[float, int, str | None]]] = defaultdict(list)
    for operation, latency_ms, rows, error in samples:
        grouped[operation].append((latency_ms, rows, error))

    result: dict[str, dict[str, Any]] = {}
    for operation, entries in sorted(grouped.items()):
        successful = [latency for latency, _, error in entries if error is None]
        errors = [error for _, _, error in entries if error is not None]
        row_counts = [rows for _, rows, error in entries if error is None]
        result[operation] = {
            "samples": len(entries),
            "successful": len(successful),
            "errors": len(errors),
            "p50_ms": percentile(successful, 0.50),
            "p95_ms": percentile(successful, 0.95),
            "p99_ms": percentile(successful, 0.99),
            "returned_rows_min": min(row_counts) if row_counts else None,
            "returned_rows_max": max(row_counts) if row_counts else None,
            "error_classes": sorted(set(errors)),
        }
    return result


def _psycopg() -> Any:
    try:
        import psycopg  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "psycopg is required; install requirements-postgres-benchmark.lock"
        ) from exc
    return psycopg


def _preflight(
    dsn: str,
    *,
    expected_branch_id: str,
    dataset_scale: int,
    writers: int,
) -> dict[str, Any]:
    psycopg = _psycopg()
    with psycopg.connect(
        dsn,
        application_name="argus-benchmark-preflight",
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_setting('neon.project_id', true), "
                "current_setting('neon.branch_id', true), count(*) "
                "FROM argus.tender GROUP BY 1, 2"
            )
            project_id, branch_id, row_count = cursor.fetchone()
            if branch_id != expected_branch_id:
                raise RuntimeError(
                    f"branch guard failed: expected {expected_branch_id}, connected to {branch_id}"
                )
            if row_count < dataset_scale:
                raise RuntimeError(
                    f"dataset guard failed: expected at least {dataset_scale} rows, found {row_count}"
                )
            if writers:
                writer_ids = [f"BENCH-TND-{index + 1:06d}" for index in range(writers)]
                cursor.execute(
                    "SELECT count(*) FROM argus.tender WHERE canonical_tender_id = ANY(%s)",
                    (writer_ids,),
                )
                found = cursor.fetchone()[0]
                if found != writers:
                    raise RuntimeError(
                        f"writer fixture guard failed: expected {writers} rows, found {found}"
                    )
        connection.rollback()
    return {"project_id": project_id, "branch_id": branch_id, "row_count": row_count}


def _run_reader(
    dsn: str,
    duration: int,
    ready: threading.Barrier,
    output: queue.SimpleQueue[Sample],
) -> None:
    psycopg = _psycopg()
    with psycopg.connect(
        dsn,
        application_name="argus-benchmark-reader",
        connect_timeout=10,
    ) as connection:
        ready.wait(timeout=60)
        stop_at = time.monotonic() + duration
        iteration = 0
        while time.monotonic() < stop_at:
            operation, sql, params = READ_QUERIES[iteration % len(READ_QUERIES)]
            iteration += 1
            started = time.perf_counter()
            error = None
            rows = 0
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SET TRANSACTION READ ONLY")
                    cursor.execute(sql, params)
                    rows = len(cursor.fetchall())
            except Exception as exc:  # failures are measurements, not omissions
                error = type(exc).__name__
            finally:
                connection.rollback()
            output.put((operation, (time.perf_counter() - started) * 1_000, rows, error))


def _run_writer(
    dsn: str,
    row_id: str,
    duration: int,
    ready: threading.Barrier,
    output: queue.SimpleQueue[Sample],
) -> None:
    psycopg = _psycopg()
    with psycopg.connect(
        dsn,
        application_name="argus-benchmark-writer",
        connect_timeout=10,
    ) as connection:
        ready.wait(timeout=60)
        stop_at = time.monotonic() + duration
        while time.monotonic() < stop_at:
            started = time.perf_counter()
            error = None
            rows = 0
            try:
                with connection.cursor() as cursor:
                    cursor.execute(WRITE_SQL, (row_id,))
                    rows = cursor.rowcount
            except Exception as exc:
                error = type(exc).__name__
            finally:
                connection.rollback()
            output.put(("rollback_update", (time.perf_counter() - started) * 1_000, rows, error))


def run_scenario(
    dsn: str,
    *,
    readers: int,
    writers: int,
    duration: int,
) -> tuple[dict[str, Any], float]:
    workers = readers + writers
    ready = threading.Barrier(workers + 1)
    output: queue.SimpleQueue[Sample] = queue.SimpleQueue()
    started = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(_run_reader, dsn, duration, ready, output)
            for _ in range(readers)
        ]
        futures.extend(
            executor.submit(
                _run_writer,
                dsn,
                f"BENCH-TND-{writer + 1:06d}",
                duration,
                ready,
                output,
            )
            for writer in range(writers)
        )
        ready.wait(timeout=60)
        for future in futures:
            future.result()

    samples: list[Sample] = []
    while not output.empty():
        samples.append(output.get())
    return summarize_samples(samples), (time.perf_counter() - started)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-branch-id", required=True)
    parser.add_argument("--dataset-scale", type=int, choices=(10_000, 100_000, 1_000_000), required=True)
    parser.add_argument("--cache-state", choices=("warm", "cold"), required=True)
    parser.add_argument("--readers", type=int, choices=(1, 8, 32), required=True)
    parser.add_argument("--writers", type=int, choices=(0, 1, 4), required=True)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--git-commit", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--enable-rollback-writes",
        action="store_true",
        help="required when writers are non-zero; updates are always rolled back",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.duration < 1:
        raise SystemExit("--duration must be positive")
    if args.writers and not args.enable_rollback_writes:
        raise SystemExit("--enable-rollback-writes is required when --writers is non-zero")
    dsn = os.environ.get("ARGUS_BENCHMARK_DSN", "").strip()
    if not dsn:
        raise SystemExit("ARGUS_BENCHMARK_DSN is required")

    environment = _preflight(
        dsn,
        expected_branch_id=args.expected_branch_id,
        dataset_scale=args.dataset_scale,
        writers=args.writers,
    )
    started_at = datetime.now(timezone.utc)
    operations, wall_seconds = run_scenario(
        dsn,
        readers=args.readers,
        writers=args.writers,
        duration=args.duration,
    )
    report = {
        "version": "1.0.0",
        "started_at_utc": started_at.isoformat(),
        "git_commit": args.git_commit,
        "dataset_scale": args.dataset_scale,
        "cache_state": args.cache_state,
        "reader_concurrency": args.readers,
        "writer_concurrency": args.writers,
        "duration_seconds": args.duration,
        "wall_seconds": round(wall_seconds, 3),
        "write_persistence": "ROLLBACK_ONLY",
        "environment": environment,
        "operations": operations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
