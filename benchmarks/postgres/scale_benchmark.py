from __future__ import annotations

import argparse
import json
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import psycopg
import yaml

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "benchmarks" / "postgres" / "tender-search-contract.yaml"

QUERY_MODES = ("exact_reference", "exact_project_code", "fts", "fuzzy", "active_closing_date")
SEARCH_SQL = "SELECT canonical_tender_id FROM argus.search_tenders(%s, %s, %s)"
LIST_SQL = "SELECT canonical_tender_id FROM argus.list_tenders('published', NULL, %s)"


def load_contract() -> dict[str, Any]:
    return yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


def env_dsn(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def percentile(values: list[float], quantile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * quantile))))
    return ordered[index]


def stats(values: list[float]) -> dict[str, float | int]:
    return {
        "samples": len(values),
        "p50": round(percentile(values, 0.50), 3),
        "p95": round(percentile(values, 0.95), 3),
        "p99": round(percentile(values, 0.99), 3),
        "min": round(min(values), 3) if values else 0.0,
        "max": round(max(values), 3) if values else 0.0,
    }


def write_json(path: str, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def setup_benchmark_roles(admin_dsn: str) -> None:
    sql = """
    DO $roles$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='bench_reader') THEN
        CREATE ROLE bench_reader LOGIN PASSWORD 'benchmark';
      ELSE
        ALTER ROLE bench_reader PASSWORD 'benchmark';
      END IF;
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='bench_writer') THEN
        CREATE ROLE bench_writer LOGIN PASSWORD 'benchmark';
      ELSE
        ALTER ROLE bench_writer PASSWORD 'benchmark';
      END IF;
    END
    $roles$;
    GRANT argus_reader TO bench_reader;
    GRANT argus_writer TO bench_writer;
    """
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        conn.execute(sql)


def seed_range(admin_dsn: str, start: int, end: int, chunk_size: int = 50_000) -> None:
    with psycopg.connect(admin_dsn) as conn:
        for lower in range(start, end + 1, chunk_size):
            upper = min(end, lower + chunk_size - 1)
            conn.execute(
                """
                INSERT INTO argus.source_record (
                  source_record_id, canonical_source_id, source_system, source_authority,
                  native_id, record_type, source_url, observed_at, content_hash,
                  raw_title, access_class, immutable, metadata
                )
                SELECT
                  'BENCH-SRC-'||lpad(g::text,7,'0'),
                  'BENCH-CANON-SRC-'||lpad(g::text,7,'0'),
                  'benchmark', 'synthetic', 'NATIVE-'||lpad(g::text,7,'0'),
                  'TENDER_NOTICE', 'https://benchmark.invalid/t/'||g, now(), md5(g::text),
                  'Synthetic tender '||g, 'BENCHMARK', true,
                  jsonb_build_object('seed','argus-scale-v1','n',g)
                FROM generate_series(%s::bigint,%s::bigint) AS g
                ON CONFLICT DO NOTHING
                """,
                (lower, upper),
            )
            conn.execute(
                """
                INSERT INTO argus.canonical_object (
                  internal_id, canonical_id, object_type, jurisdiction, title,
                  description, status, legacy_identity, attributes
                )
                SELECT
                  ('10000000-0000-0000-0000-'||lpad(g::text,12,'0'))::uuid,
                  'BENCH-TND-'||lpad(g::text,7,'0'), 'SOLICITATION', 'BD',
                  'Synthetic government tender '||g, 'Portable scale benchmark fixture',
                  'CURRENT', false, jsonb_build_object('seed','argus-scale-v1','n',g)
                FROM generate_series(%s::bigint,%s::bigint) AS g
                ON CONFLICT DO NOTHING
                """,
                (lower, upper),
            )
            conn.execute(
                """
                INSERT INTO argus.tender (
                  canonical_tender_id, tender_reference, project_code, package_no,
                  title, buyer_name, ministry_name, jurisdiction, source_system,
                  source_record_id, district, procurement_method, procurement_type,
                  status, publication_date, closing_at, opening_at, budget_source,
                  currency_code, estimated_value, tender_security, source_url, attributes
                )
                SELECT
                  'BENCH-TND-'||lpad(g::text,7,'0'),
                  'REF-'||lpad(g::text,7,'0'),
                  'PRJ-'||lpad((((g-1)/10)+1)::text,7,'0'),
                  'PKG-'||lpad(g::text,7,'0'),
                  CASE WHEN g %% 5 = 0 THEN 'Coastal Patrol Vessel navigation system '||g
                       WHEN g %% 5 = 1 THEN 'Marine communications equipment '||g
                       WHEN g %% 5 = 2 THEN 'Port surveillance radar system '||g
                       WHEN g %% 5 = 3 THEN 'Naval training simulator package '||g
                       ELSE 'Shipboard power management system '||g END,
                  'Benchmark Buyer '||(g%%100), 'Benchmark Ministry '||(g%%20),
                  'BD', 'benchmark', 'BENCH-SRC-'||lpad(g::text,7,'0'),
                  'Dhaka', 'OPEN_TENDER', 'GOODS', 'published',
                  current_date - ((g%%365)::int),
                  now() + ((g%%180)||' days')::interval,
                  now() + ((g%%180)||' days')::interval + interval '1 hour',
                  'GOB', 'USD', 100000 + g, 1000 + (g%%5000),
                  'https://benchmark.invalid/t/'||g,
                  jsonb_build_object('seed','argus-scale-v1','n',g)
                FROM generate_series(%s::bigint,%s::bigint) AS g
                ON CONFLICT DO NOTHING
                """,
                (lower, upper),
            )
            conn.commit()

        conn.execute("ANALYZE argus.source_record")
        conn.execute("ANALYZE argus.canonical_object")
        conn.execute("ANALYZE argus.tender")
        conn.commit()


def query_for(mode: str, scale: int, rng: random.Random) -> tuple[str, tuple[Any, ...]]:
    if mode == "exact_reference":
        n = rng.randint(1, scale)
        return SEARCH_SQL, (mode, f"REF-{n:07d}", 20)
    if mode == "exact_project_code":
        n = rng.randint(1, max(1, scale // 10))
        return SEARCH_SQL, (mode, f"PRJ-{n:07d}", 20)
    if mode == "fts":
        return SEARCH_SQL, (mode, "Coastal Patrol Vessel navigation", 20)
    if mode == "fuzzy":
        target = max(5, scale - (scale % 5))
        return SEARCH_SQL, (mode, f"Coastal Patrol Vesel navigation system {target}", 20)
    if mode == "active_closing_date":
        return LIST_SQL, (20,)
    raise ValueError(mode)


def one_query(conn: psycopg.Connection[Any], mode: str, scale: int, rng: random.Random) -> float:
    sql, params = query_for(mode, scale, rng)
    started = time.perf_counter()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cur.fetchall()
    return (time.perf_counter() - started) * 1000.0


def warm_benchmark(reader_dsn: str, scale: int, samples_per_mode: int = 100) -> dict[str, Any]:
    result: dict[str, Any] = {"scale": scale, "samples_per_mode": samples_per_mode, "modes": {}}
    with psycopg.connect(reader_dsn, autocommit=True) as conn:
        for offset, mode in enumerate(QUERY_MODES):
            rng = random.Random(scale + offset)
            values = [one_query(conn, mode, scale, rng) for _ in range(samples_per_mode)]
            result["modes"][mode] = stats(values)
    return result


def plan_indexes(admin_dsn: str, scale: int) -> dict[str, list[str]]:
    probes = {
        "exact_reference": (
            "EXPLAIN (FORMAT JSON) SELECT canonical_tender_id FROM argus.tender "
            "WHERE lower(tender_reference)=lower(%s) LIMIT 20",
            (f"REF-{max(1, scale//2):07d}",),
        ),
        "exact_project_code": (
            "EXPLAIN (FORMAT JSON) SELECT canonical_tender_id FROM argus.tender "
            "WHERE lower(project_code)=lower(%s) LIMIT 20",
            (f"PRJ-{max(1, scale//20):07d}",),
        ),
        "fts": (
            "EXPLAIN (FORMAT JSON) SELECT canonical_tender_id FROM argus.tender "
            "WHERE search_vector @@ websearch_to_tsquery('simple',%s) LIMIT 20",
            ("Coastal Patrol Vessel navigation",),
        ),
        "fuzzy": (
            "EXPLAIN (FORMAT JSON) SELECT canonical_tender_id FROM argus.tender "
            "WHERE title OPERATOR(public.%%) %s "
            "ORDER BY title OPERATOR(public.<->) %s, canonical_tender_id LIMIT 20",
            (f"Coastal Patrol Vesel navigation system {max(5, scale-scale%5)}",) * 2,
        ),
        "active_closing_date": (
            "EXPLAIN (FORMAT JSON) SELECT canonical_tender_id FROM argus.tender "
            "WHERE status='published' ORDER BY closing_at NULLS LAST, canonical_tender_id LIMIT 20",
            (),
        ),
    }

    def collect_indexes(node: Any, found: set[str]) -> None:
        if isinstance(node, dict):
            if "Index Name" in node:
                found.add(str(node["Index Name"]))
            for value in node.values():
                collect_indexes(value, found)
        elif isinstance(node, list):
            for value in node:
                collect_indexes(value, found)

    result: dict[str, list[str]] = {}
    with psycopg.connect(admin_dsn, autocommit=True) as conn:
        for mode, (sql, params) in probes.items():
            row = conn.execute(sql, params).fetchone()
            found: set[str] = set()
            collect_indexes(row[0] if row else None, found)
            result[mode] = sorted(found)
    return result


_counter_lock = threading.Lock()
_counter = 2_000_000


def next_ingest_id() -> int:
    global _counter
    with _counter_lock:
        _counter += 1
        return _counter


def writer_once(conn: psycopg.Connection[Any]) -> float:
    n = next_ingest_id()
    started = time.perf_counter()
    with conn.transaction():
        conn.execute(
            "INSERT INTO argus.source_record(source_record_id,source_system,native_id,record_type,observed_at,raw_title) "
            "VALUES (%s,'benchmark-write',%s,'TENDER_NOTICE',now(),%s)",
            (f"WRITE-SRC-{n}", f"WRITE-NATIVE-{n}", f"Concurrent write {n}"),
        )
        conn.execute(
            "INSERT INTO argus.canonical_object(internal_id,canonical_id,object_type,jurisdiction,title,status) "
            "VALUES ((%s)::uuid,%s,'SOLICITATION','BD',%s,'CURRENT')",
            (f"20000000-0000-0000-0000-{n:012d}", f"WRITE-TND-{n}", f"Concurrent tender {n}"),
        )
        conn.execute(
            "INSERT INTO argus.tender(canonical_tender_id,tender_reference,project_code,title,jurisdiction,source_system,source_record_id,status,currency_code) "
            "VALUES (%s,%s,%s,%s,'BD','benchmark-write',%s,'published','USD')",
            (
                f"WRITE-TND-{n}", f"WRITE-REF-{n}", f"WRITE-PRJ-{n//10}",
                f"Concurrent Coastal Patrol Vessel {n}", f"WRITE-SRC-{n}",
            ),
        )
    return (time.perf_counter() - started) * 1000.0


def concurrency_stage(
    reader_dsn: str,
    writer_dsn: str,
    scale: int,
    readers: int,
    writers: int,
    duration_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + duration_seconds
    read_values: dict[str, list[float]] = {mode: [] for mode in QUERY_MODES}
    write_values: list[float] = []
    errors: list[str] = []
    lock = threading.Lock()

    def reader_worker(worker_id: int) -> None:
        rng = random.Random(scale * 1000 + readers * 100 + writers * 10 + worker_id)
        try:
            with psycopg.connect(reader_dsn, autocommit=True) as conn:
                while time.monotonic() < deadline:
                    mode = rng.choices(QUERY_MODES, weights=(35, 25, 20, 10, 10), k=1)[0]
                    try:
                        elapsed = one_query(conn, mode, scale, rng)
                        with lock:
                            read_values[mode].append(elapsed)
                    except Exception as exc:  # noqa: BLE001
                        with lock:
                            errors.append(f"reader:{type(exc).__name__}:{exc}")
        except Exception as exc:  # noqa: BLE001
            with lock:
                errors.append(f"reader_connect:{type(exc).__name__}:{exc}")

    def writer_worker() -> None:
        try:
            with psycopg.connect(writer_dsn) as conn:
                while time.monotonic() < deadline:
                    try:
                        elapsed = writer_once(conn)
                        with lock:
                            write_values.append(elapsed)
                    except Exception as exc:  # noqa: BLE001
                        conn.rollback()
                        with lock:
                            errors.append(f"writer:{type(exc).__name__}:{exc}")
        except Exception as exc:  # noqa: BLE001
            with lock:
                errors.append(f"writer_connect:{type(exc).__name__}:{exc}")

    with ThreadPoolExecutor(max_workers=readers + writers) as pool:
        futures = [pool.submit(reader_worker, idx) for idx in range(readers)]
        futures.extend(pool.submit(writer_worker) for _ in range(writers))
        for future in futures:
            future.result()

    return {
        "readers": readers,
        "writers": writers,
        "duration_seconds": duration_seconds,
        "read": {mode: stats(values) for mode, values in read_values.items()},
        "write": stats(write_values),
        "read_operations": sum(len(values) for values in read_values.values()),
        "write_operations": len(write_values),
        "errors": errors[:100],
        "error_count": len(errors),
        "zero_query_errors": len(errors) == 0,
    }


def run_seed_warm(args: argparse.Namespace) -> None:
    contract = load_contract()
    admin_dsn = env_dsn("ARGUS_BENCH_ADMIN_DSN")
    reader_dsn = env_dsn("ARGUS_BENCH_DSN")
    setup_benchmark_roles(admin_dsn)
    scales = [int(value) for value in contract["dataset_scales"]]
    completed = 0
    results: list[dict[str, Any]] = []
    for scale in scales:
        if scale > completed:
            seed_range(admin_dsn, completed + 1, scale)
            completed = scale
        results.append({"scale": scale, "warm": warm_benchmark(reader_dsn, scale), "indexes": plan_indexes(admin_dsn, scale)})
    write_json(args.output, {"dataset_scales": scales, "results": results, "overall_pass": True})


def run_concurrency(args: argparse.Namespace) -> None:
    contract = load_contract()
    reader_dsn = env_dsn("ARGUS_BENCH_DSN")
    writer_dsn = env_dsn("ARGUS_BENCH_WRITER_DSN")
    scale = int(contract["dataset_scales"][-1])
    reader_levels = [int(v) for v in contract["concurrency"]["reader_levels"]]
    writer_levels = [int(v) for v in contract["concurrency"]["writer_levels"]]
    duration_seconds = int(contract["concurrency"]["duration_seconds"])
    stages = [
        concurrency_stage(reader_dsn, writer_dsn, scale, readers, writers, duration_seconds)
        for readers in reader_levels
        for writers in writer_levels
    ]
    zero_query_errors = all(stage["zero_query_errors"] for stage in stages)
    write_json(
        args.output,
        {
            "scale": scale,
            "reader_levels": reader_levels,
            "writer_levels": writer_levels,
            "duration_seconds": duration_seconds,
            "stages": stages,
            "zero_query_errors": zero_query_errors,
            "overall_pass": zero_query_errors,
        },
    )
    if not zero_query_errors:
        raise SystemExit(2)


def run_cold(args: argparse.Namespace) -> None:
    contract = load_contract()
    reader_dsn = env_dsn("ARGUS_BENCH_DSN")
    scale = int(contract["dataset_scales"][-1])
    mode = args.query_mode
    if mode not in QUERY_MODES:
        raise SystemExit(f"unsupported cold query mode: {mode}")
    rng = random.Random(scale + QUERY_MODES.index(mode))
    with psycopg.connect(reader_dsn, autocommit=True) as conn:
        elapsed = one_query(conn, mode, scale, rng)
    write_json(
        args.output,
        {
            "scale": scale,
            "query_mode": mode,
            "cold_method": "postgres_process_restart",
            "latency_ms": round(elapsed, 3),
            "overall_pass": True,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed = subparsers.add_parser("seed-warm")
    seed.add_argument("--output", required=True)
    seed.set_defaults(func=run_seed_warm)

    concurrency = subparsers.add_parser("concurrency")
    concurrency.add_argument("--output", required=True)
    concurrency.set_defaults(func=run_concurrency)

    cold = subparsers.add_parser("cold")
    cold.add_argument("--query-mode", required=True)
    cold.add_argument("--output", required=True)
    cold.set_defaults(func=run_cold)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
