# Live runtime testing

ARGUS provides a self-contained smoke exercise over the real
`Argus.analyze(AnalysisEnvelope)` interface:

```bash
python -m pip install --require-hashes -r requirements-test.lock
python -m tools.live_smoke
```

The command creates a current schema-valid ATLAS handoff, generates an
ephemeral Ed25519 key in memory, signs the handoff, executes the governed ARGUS
runtime, validates result correlation, and reaches a `RETURNED` synchronization
receipt. The private key is not written anywhere.

Compact text is the low-overhead default. For a machine consumer, NDJSON emits
one started event and one result event, flushing each line independently:

```bash
python -m tools.live_smoke --format ndjson
```

This proves local schema, authentication, synchronization, domain-method, and
result-correlation wiring. It intentionally performs no network collection,
uses no production key, and writes nothing to the Master Registry. It does not
prove autonomous source acquisition, production key distribution, branch
protection, or live ChatGPT/Work deployment.

## Real cross-repository test

Place compatible checkouts beside one another and run from the ARGUS root:

```text
parent/
├── atlas-os/
└── argus-intelligence/
```

```bash
python -m tools.cross_repo_e2e --atlas-repo ../atlas-os
python -m tools.cross_repo_e2e --atlas-repo ../atlas-os --format ndjson
python -m unittest discover -s tests/cross_repo -v
```

The command rejects an ATLAS checkout whose Git commit or manifest version
does not exactly match the ARGUS compatibility descriptor. With the correct
checkout it executes these real public seams:

```text
ATLAS execute + classify + align + handoff + route + attest
  → ARGUS analyze + correlate + return
  → ATLAS verify returned handoff receipt
```

It generates an ephemeral key in memory, performs no network collection and
makes no registry write. This verifies the two codebases together; it still
does not provide production key governance, external ChatGPT/Work evidence,
or autonomous intelligence acquisition.

The automatic `Cross-repository E2E` GitHub workflow runs the same test on
compatibility-boundary pull requests and pushes to `main`, and can also be run
manually. Because both repositories are private, ATLAS is checked out through a
repository-scoped read-only deploy key. Its private half is stored only in the
ARGUS Actions secret `ATLAS_SSH_KEY`; the ATLAS deploy key has read-only access,
and the normal repository token is intentionally not broadened.
