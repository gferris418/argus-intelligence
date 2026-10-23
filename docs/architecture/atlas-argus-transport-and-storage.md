# ATLAS–ARGUS transport and storage standard

## Decision

ATLAS and ARGUS use the narrowest protocol that preserves the required boundary.

| Boundary | Standard |
|---|---|
| ChatGPT or agent host to ATLAS tools | MCP |
| ATLAS to ARGUS in the same process | Native typed provider call |
| ATLAS to a separately deployed ARGUS service | Connect RPC or gRPC with Protobuf |
| ARGUS to PostgreSQL | Pooled native driver with parameterized calls to admitted database functions |
| Long-running collection | Durable queue plus transactional outbox and idempotent job API |
| Progress delivery | SSE or WebSocket over the durable job state |
| Documents and large artifacts | Object storage reference with digest, media type, authorization and expiry |

Connect/gRPC is not introduced merely for conceptual uniformity. The current provider adapter is in-process, so a native typed call is both faster and easier to verify. A network transport is admitted only when ATLAS and ARGUS are separately deployed or independently scaled.

## Network-boundary prerequisites

Before a remote ARGUS endpoint is admitted, the request envelope must bind:

- contract version;
- ATLAS task and approval identifiers;
- approved scope digest;
- issued-at and expiry times;
- idempotency key;
- caller and provider identities;
- replay protection;
- deadline and cancellation semantics.

Transport authentication must use workload identity or mutual TLS. A plain `approval_status: APPROVED` field is sufficient only inside the current trusted in-process boundary.

## Database boundary

The PostgreSQL owner role is for migrations only. Runtime retrieval uses `argus.search_tenders` and `argus.list_tenders` through the `argus_reader` capability role. Ingestion uses `argus_writer`. Neither runtime capability receives delete or truncate authority.

The search functions enforce explicit projections, a two-second statement timeout and a result limit from 1 through 100. Search routing remains:

1. exact tender reference;
2. exact project code;
3. structured status/buyer/date lookup;
4. full-text search;
5. fuzzy search only as an explicit fallback.

Raw table access is not part of the reader contract.

## Long-running work

SSE and WebSocket are delivery transports, not durable queues. A large collection request returns a job identifier, persists its state before acknowledgement, and emits progress from durable state. Completion returns an intelligence collection package to ATLAS for schema validation and reconciliation.
