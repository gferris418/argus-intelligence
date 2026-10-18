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
