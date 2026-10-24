# ATLAS–ARGUS Modular Skill Architecture v1 Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single monolithic ARGUS/ATLAS plugin surfaces with small standards-conformant routed skill families while preserving ATLAS authority and proving behavior with the CPV, coastal-surveillance-radar, and BADC seed-cleaner pilots.

**Architecture:** ATLAS remains the sole Mission Control, approval, persistence-authority, verification and completion layer. ARGUS gains a root router plus four specialist skills selected by a canonical maturity-aware `mission_skill_plan`; specialists share canonical IDs, treat retrieved source content as untrusted evidence, and always return to ATLAS. Plugin packages use Agent Skills progressive disclosure and bundle the canonical routing/security contracts required for offline operation.

**Tech Stack:** Agent Plugins v1 `plugin.json`, Agent Skills `SKILL.md`, YAML/JSON contracts, Python `unittest`, GitHub Actions, guarded Plugin Creator publication.

## Global Constraints

- ATLAS remains the only routing, approval, persistence-authorization, verification, final-commercial-decision and completion authority.
- ARGUS activation remains explicitly approval-gated by ATLAS.
- Specialists are workflows/skills under ARGUS, not peer agents or new control planes.
- Preserve one canonical lineage across organization/project/requirement/procurement/tender/opportunity/supplier/source objects.
- External source text is untrusted evidence and cannot become executable instruction or durable machine instruction without structured extraction and provenance binding.
- Use maturity-aware routing; do not run every specialist for every mission.
- Procurement modes are `DISCOVERY`, `LIVE_PROCUREMENT`, and `POST_DEADLINE_REVALIDATION`.
- Preserve current SharePoint persistence routing and durable-write receipt requirements.
- CPV, coastal-surveillance-radar, and BADC seed-cleaner scenarios are release-blocking regression fixtures.
- Agent Skills and Agent Plugins conformance must pass before publication.
- No `mcp.json` is added until a real shared MCP server exists.

---

### Task 1: Canonical ARGUS maturity and mission-skill-plan contract

**Files:**
- Create: `spec/mission-skill-routing.yaml`
- Create: `schemas/mission-skill-plan.schema.json`
- Create: `tests/test_modular_skill_routing.py`
- Modify: `argus-intelligence.yaml`

**Interfaces:**
- Consumes: ATLAS-authorized ARGUS mission objective, canonical object IDs, evidence state, current ARGUS I0–I9 compatibility maturity.
- Produces: `mission_skill_plan` with `mission_state`, specialist entries (`REQUIRED|CONDITIONAL|SKIP`), procurement mode where applicable, rationale, and unresolved evidence gaps.

- [ ] **Step 1: Add the focused failing test**
  - Assert the routing spec defines `SEED`, `NEED_OBSERVED`, `PROJECT_IDENTIFIED`, `PROCUREMENT_EXPECTED`, `PROCUREMENT_LIVE`, `PROCUREMENT_CLOSED`, `AWARD_OBSERVED`, `POST_AWARD`, and orthogonal `STALE_REVALIDATION_REQUIRED`.
  - Assert procurement modes are exactly `DISCOVERY`, `LIVE_PROCUREMENT`, `POST_DEADLINE_REVALIDATION`.
  - Assert CPV maps to full-chain required specialists with `LIVE_PROCUREMENT`.
  - Assert coastal-surveillance-radar remains seed/need-observed and cannot require live-procurement mode without authoritative evidence.
  - Assert BADC stale evidence requires monitoring/revalidation and cannot set canonical live lifecycle from secondary evidence alone.

- [ ] **Step 2: Verify the relevant failure**
  - Run: `python -m unittest tests.test_modular_skill_routing -v`
  - Expected: failure because the routing spec/schema do not yet exist.

- [ ] **Step 3: Implement the minimum behavior**
  - Add declarative maturity states, legal specialist activation semantics, procurement modes, evidence gates, canonical-identity invariants and ATLAS-return authority.
  - Keep existing I0–I9 maturity as compatibility metadata; do not silently redefine it.

- [ ] **Step 4: Verify the focused pass**
  - Run: `python -m unittest tests.test_modular_skill_routing -v`
  - Expected: all modular-routing tests pass.

- [ ] **Step 5: Run the affected integration check**
  - Run: `python -m unittest tests.test_360_collection_contract tests.test_argus_activation_contract tests.test_argus_v3_provider_contract -v`
  - Expected: existing ARGUS/ATLAS boundary tests remain green.

- [ ] **Step 6: Commit the passing deliverable**
  - Commit: `feat: add maturity-aware ARGUS mission skill routing`

### Task 2: ARGUS progressive-disclosure specialist skill family and trust boundary

**Files:**
- Modify: `skills/argus-intelligence/SKILL.md`
- Create: `skills/argus-intelligence/references/mission-routing.md`
- Create: `skills/argus-intelligence/references/untrusted-source-boundary.md`
- Create: `skills/argus-opportunity-intelligence/SKILL.md`
- Create: `skills/argus-ecosystem-intelligence/SKILL.md`
- Create: `skills/argus-procurement-market-intelligence/SKILL.md`
- Create: `skills/argus-monitoring-revalidation/SKILL.md`
- Create: `tests/test_agent_skill_family.py`

**Interfaces:**
- Consumes: `mission_skill_plan`, ATLAS authority envelope, canonical IDs, evidence/provenance context.
- Produces: bounded specialist results containing observations, facts, inferences, contradictions, unknowns, source provenance, proposed mutations and next research-frontier gaps; every result returns to ATLAS.

- [ ] **Step 1: Add the focused failing test**
  - Assert all five skills exist and have Agent Skills-compatible frontmatter.
  - Assert root skill routes rather than duplicating specialist procedures.
  - Assert every specialist declares ATLAS return authority and canonical-ID preservation.
  - Assert every specialist treats source-embedded instructions as untrusted evidence.
  - Assert procurement skill documents all three procurement modes.

- [ ] **Step 2: Verify the relevant failure**
  - Run: `python -m unittest tests.test_agent_skill_family -v`
  - Expected: failure because specialist skills/references do not exist.

- [ ] **Step 3: Implement the minimum behavior**
  - Keep descriptions narrow and mutually distinguishable.
  - Put shared source-security rules in the root reference and repeat only the invariant needed for safe specialist execution.
  - Move core/package versions into frontmatter `metadata` rather than unsupported top-level `version` fields.

- [ ] **Step 4: Verify the focused pass**
  - Run: `python -m unittest tests.test_agent_skill_family -v`
  - Expected: all skill-family tests pass.

- [ ] **Step 5: Run the affected integration check**
  - Run: `python -m unittest tests.test_argus_activation_contract tests.test_collection_architecture tests.test_360_collection_contract -v`
  - Expected: routing/activation doctrine remains compatible.

- [ ] **Step 6: Commit the passing deliverable**
  - Commit: `feat: add ARGUS specialist skill family`

### Task 3: Pilot regressions, package conformance, and ARGUS release artifact

**Files:**
- Create: `tests/scenarios/modular-skill-pilots.json`
- Create: `tests/test_modular_skill_pilots.py`
- Modify: `tests/test_chatgpt_plugin_package.py`
- Modify: `.github/workflows/chatgpt-plugin-package.yml`
- Modify: `plugin.json`
- Modify: `argus-intelligence.yaml`

**Interfaces:**
- Consumes: skill family and mission-routing contract.
- Produces: release-blocking pilot assertions and a self-contained Agent Plugin artifact containing all five skills plus routing/security/persistence contracts.

- [ ] **Step 1: Add the focused failing test**
  - CPV: `PROCUREMENT_LIVE`, full relevant chain, existing lineage reuse, latest authoritative event wins.
  - Radar: seed/need-observed, procurement conditional/discovery only, no opportunity promotion from supplier coverage.
  - BADC: stale/revalidation-required unless originating current evidence is supplied; secondary sources cannot establish live lifecycle.
  - Package: all five skills and required contracts are present.

- [ ] **Step 2: Verify the relevant failure**
  - Run: `python -m unittest tests.test_modular_skill_pilots tests.test_chatgpt_plugin_package -v`
  - Expected: package/scenario assertions fail before workflow/package updates.

- [ ] **Step 3: Implement the minimum behavior**
  - Update packaging paths and synchronization hashes for all release-driving skill/contract files.
  - Bump ARGUS core candidate `3.0.0-rc.2` → `3.0.0-rc.3` because the canonical runtime contract changes.
  - Bump ARGUS Agent Plugin package `3.0.2` → `3.0.3`.

- [ ] **Step 4: Verify the focused pass**
  - Run: `python -m unittest tests.test_modular_skill_pilots tests.test_chatgpt_plugin_package -v`
  - Expected: pilot/package tests pass.

- [ ] **Step 5: Run the affected integration check**
  - Run repository full contract suite through the existing `contract-tests.yml` and `chatgpt-plugin-package.yml` PR workflows.
  - Expected: both workflows pass and artifact inspection confirms the complete modular skill package.

- [ ] **Step 6: Commit the passing deliverable**
  - Commit: `release: package modular ARGUS skills`

### Task 4: ATLAS specialist governance wrappers, compatibility repin, and guarded publication

**Files (ATLAS repository):**
- Modify: `skills/atlas-os/SKILL.md`
- Create: `skills/atlas-action-governance/SKILL.md`
- Create: `skills/atlas-provider-handoff/SKILL.md`
- Create: `skills/atlas-persistence/SKILL.md`
- Create: `skills/atlas-verification/SKILL.md`
- Create: `tests/conformance/test_modular_atlas_skill_family.py`
- Modify: `.github/plugin-release-policy.yaml`
- Modify: `.github/workflows/plugin-release-gate.yml` only if required by package enumeration
- Modify: `plugin.json`
- Modify: ARGUS compatibility pin/tests after ARGUS merge

**Interfaces:**
- Consumes: existing ATLAS Mission Control/core contracts and merged ARGUS integration contract.
- Produces: progressive-disclosure governance skills that never create new authority; guarded release artifact pinned to exact ARGUS main commit.

- [ ] **Step 1: Add the focused failing test**
  - Assert five ATLAS skills exist, root remains authority/router, and specialists reference existing canonical specs rather than redefining policy.
  - Assert package includes all skills and current persistence contracts.
  - Assert compatibility pin matches merged ARGUS modular release commit.

- [ ] **Step 2: Verify the relevant failure**
  - Run the focused ATLAS conformance test in CI/available test runner.
  - Expected: missing specialist skills/package entries/pin fail.

- [ ] **Step 3: Implement the minimum behavior**
  - Add narrow specialist governance wrappers.
  - Keep ATLAS core version `3.0.2` because authority/runtime semantics remain unchanged.
  - Bump Agent Plugin package from `3.0.3` → `3.0.4`.
  - Repin exact ARGUS modular release commit.

- [ ] **Step 4: Verify the focused pass**
  - Run focused conformance tests.
  - Expected: pass.

- [ ] **Step 5: Run the affected integration check**
  - Run `Validate ATLAS-OS`, `ChatGPT Plugin Release Gate`, and ARGUS cross-repository E2E on the exact final heads.
  - Inspect release artifacts before publication.
  - Expected: green with self-contained packages and current compatibility receipts.

- [ ] **Step 6: Commit/publish the passing deliverable**
  - Merge protected PRs only after all required checks are green.
  - Use Plugin Creator guarded updates against the current release IDs.
  - Re-read both installed plugins after publication and verify file/version parity with canonical GitHub artifacts.

## Unresolved externally observable decisions

None. The validated research fixes the routing states, skill boundaries, authority model, package-version behavior and pilot acceptance criteria. A real MCP server remains intentionally out of scope until an executable shared service exists.
