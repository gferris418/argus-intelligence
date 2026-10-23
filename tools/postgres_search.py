from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Mapping, Sequence


_TENDER_PROJECTION = (
    "canonical_tender_id, tender_reference, project_code, title, buyer_name, "
    "status, closing_at, source_url, score"
)
_SEARCH_SQL = f"SELECT {_TENDER_PROJECTION} FROM argus.search_tenders(%s, %s, %s)"


@dataclass(frozen=True)
class TenderSearchConfig:
    statement_timeout_ms: int = 2_000
    maximum_limit: int = 100

    def __post_init__(self) -> None:
        if not isinstance(self.statement_timeout_ms, int) or self.statement_timeout_ms < 1:
            raise ValueError("statement_timeout_ms must be a positive integer")
        if not isinstance(self.maximum_limit, int) or not 1 <= self.maximum_limit <= 100:
            raise ValueError("maximum_limit must be between 1 and 100")


@dataclass(frozen=True)
class TenderSearchStep:
    mode: str
    sql: str
    params: tuple[str, str, int]


@dataclass(frozen=True)
class TenderSearchResult:
    route: str
    rows: tuple[Mapping[str, Any], ...]
    latency_ms: float
    query_count: int
    telemetry: tuple[Mapping[str, Any], ...]


def _validated_query(query: str) -> str:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    return " ".join(query.split())


def _validated_limit(limit: int, maximum: int = 100) -> int:
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= maximum:
        raise ValueError(f"limit must be between 1 and {maximum}")
    return limit


def build_tender_search_steps(query: str, limit: int = 20) -> tuple[TenderSearchStep, ...]:
    normalized = _validated_query(query)
    bounded = _validated_limit(limit, 100)
    return tuple(
        TenderSearchStep(mode=mode, sql=_SEARCH_SQL, params=(mode, normalized, bounded))
        for mode in ("exact_reference", "exact_project_code", "fts", "fuzzy")
    )


def _row_mapping(description: Sequence[Any] | None, row: Any) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    names = [column[0] for column in (description or ())]
    if names and isinstance(row, Sequence) and not isinstance(row, (str, bytes, bytearray)):
        return dict(zip(names, row, strict=False))
    return {"value": row}


class TenderSearchAdapter:
    """Read-only PostgreSQL tender search with deterministic fallback and telemetry.

    The adapter never accepts caller-provided SQL. It executes only the fixed,
    explicitly projected function call above, uses bound parameters for user data,
    hard-bounds result size, applies a local statement timeout, and rolls back the
    read-only transaction after every search.
    """

    def __init__(self, config: TenderSearchConfig | None = None) -> None:
        self.config = config or TenderSearchConfig()

    def search(self, connection: Any, query: str, *, limit: int = 20) -> TenderSearchResult:
        normalized = _validated_query(query)
        bounded = _validated_limit(limit, self.config.maximum_limit)
        steps = build_tender_search_steps(normalized, bounded)
        started = perf_counter()
        telemetry: list[Mapping[str, Any]] = []
        selected_route = "none"
        rows: tuple[Mapping[str, Any], ...] = ()
        query_count = 0

        try:
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(f"SET LOCAL statement_timeout = '{self.config.statement_timeout_ms}ms'")

                for step in steps:
                    step_started = perf_counter()
                    cursor.execute(step.sql, step.params)
                    query_count += 1
                    fetched = cursor.fetchall()
                    step_latency_ms = (perf_counter() - step_started) * 1_000
                    telemetry.append(
                        {
                            "mode": step.mode,
                            "latency_ms": step_latency_ms,
                            "row_count": len(fetched),
                        }
                    )
                    if fetched:
                        selected_route = step.mode
                        rows = tuple(_row_mapping(cursor.description, row) for row in fetched)
                        break
        finally:
            # A rollback closes the read-only transaction and guarantees this adapter
            # cannot accidentally persist session work performed by its own queries.
            connection.rollback()

        return TenderSearchResult(
            route=selected_route,
            rows=rows,
            latency_ms=(perf_counter() - started) * 1_000,
            query_count=query_count,
            telemetry=tuple(telemetry),
        )


__all__ = [
    "TenderSearchAdapter",
    "TenderSearchConfig",
    "TenderSearchResult",
    "TenderSearchStep",
    "build_tender_search_steps",
]
