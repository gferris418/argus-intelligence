# Live End-to-End Dry Run — Bangladesh Coast Guard Coastal Patrol Vessel

**Scenario:** Coastal Patrol Vessel for Bangladesh Coast Guard  
**As of:** 2026-10-22  
**Status:** Autonomous-flow validation candidate  
**Purpose:** Validate the one-handoff/one-return, institution-first ARGUS workflow against a real Bangladesh Coast Guard procurement and the active ARGUS operational registry.

## Evidence baseline

### BPPA solicitation

Official procurement evidence establishes:

- Ministry/Division: Ministry of Home Affairs;
- Agency: Bangladesh Coast Guard Force;
- Procuring Entity: Project Director;
- PE Code: `224392800`;
- Invitation Reference: `44.08.2680.033.02.106.26.160`;
- Invitation For: Works;
- Procurement Method: `ICT One Stage & Two envelope Tendering Method`;
- Budget and Source: `Development Budget GOB`;
- Project/Programme Code: blank on the BPPA record;
- Project/Programme Name: blank on the BPPA record;
- Tender Package No: blank on the BPPA record;
- Tender Package Name: `Construction and Delivery of 4 (Four) in No. Coastal Patrol Vessel (CPV)`;
- Lot No: `1`;
- Lot Identification: `WD-2`;
- stated experience: at least 10 years of shipbuilding and delivery of combat vessels/patrol crafts;
- tender document price: BDT 100,000 non-refundable;
- tender security: BDT 23 crore;
- completion period: 36 months after contract signing.

Corrigendum history is append-only. The latest published corrigendum in the captured BPPA record is dated 19 October 2026 and sets:

- last selling date: 28 October 2026;
- closing: 29 October 2026, 12:00 PM;
- opening: 29 October 2026, 12:30 PM;
- status: Active.

### Active ARGUS operational registry

The current SharePoint SQLite materialization already contains the CPV lineage, including:

- procurement process `PROC-BCG-LT001`;
- derived requirement `REQ-BD-000001`;
- solicitation `TND-BD-000001`;
- lot `LOT-BD-000001`;
- item `ITM-BD-000001`;
- source record `SRC-BD-000001`;
- publication/corrigendum history.

The BPPA blank project/programme/package fields remain unknown; no upstream project/package identity is fabricated merely to complete the hierarchy.

---

## Runtime trace

### 1. User seed

Input:

`Coastal Patrol Vessel for Bangladesh Coast Guard`

ATLAS interprets this as a Bangladesh government-commercial intelligence request concerning a named public-sector end user and a specific maritime capability/product class. The seed is not itself proof of a project, procurement or new opportunity.

### 2. ATLAS three-step preprocessing

ATLAS performs only:

1. **Understand + Normalize** — normalize the subject to Coastal Patrol Vessel / Bangladesh Coast Guard.
2. **Minimal Domain Framing** — Bangladesh; maritime-security/public-sector context; named government buyer/end user; shipbuilding/vessel capability.
3. **Route** — `ARGUS_COLLECTION`.

ATLAS does not try to solve the project, funding, procurement, supplier or competitor questions itself.

### 3. One governed collection mission

ATLAS creates one collection mission with:

- `handoff_pattern = ONE_HANDOFF_ONE_RETURN`;
- `autonomy_mode = BOUNDED_AUTONOMOUS`;
- `identity_confirmation = AMBIGUOUS_ONLY`;
- `follow_evidence_leads_without_callback = true`;
- `parallel_safe_reads = true`;
- `persistence_mode = PROPOSE_BATCH_THEN_ATLAS_COMMIT`;
- `mission_context = TRANSIENT_ONLY`.

The mission authorizes research, not consequential external action or uncontrolled persistence.

### 4. ARGUS — resolve institutional hierarchy first

ARGUS establishes the evidence-supported chain:

`Bangladesh → Ministry of Home Affairs → Bangladesh Coast Guard Force → Project Director / Procuring Entity`

The published notice establishes the Ministry, Agency and PE roles. ARGUS does not silently assume additional project, directorate or operational-command nodes that the evidence does not establish.

Output:

- resolved government hierarchy;
- reusable canonical institution references;
- unresolved downstream institutional roles retained as unknown where needed.

### 5. ARGUS — check the internal canonical registry before creating anything

ARGUS searches the current operational registry using, in order where available:

1. official invitation/reference identifiers;
2. source-system identifiers;
3. buyer + procurement/requirement relationships;
4. buyer + CPV product/capability + quantity;
5. semantic similarity only as candidate evidence.

Existing CPV lineage is found.

Output:

`identity_state = EXACT / HIGH_CONFIDENCE_MATCH` (depending on the exact identifier evidence available to the runtime)

Action:

Continue on the existing lineage. **Do not ask the user whether to create another opportunity.**

If the evidence had only produced `PROBABLE_MATCH` or `UNRESOLVED`, the system would stop at this seam and ask once before a duplicate/merge-sensitive action.

### 6. ARGUS — check official procurement sources

Because the existing lineage is resolved, ARGUS checks competent Bangladesh publication sources according to the evidenced route rather than guessing the portal from the product name.

The BPPA notice confirms a formal procurement for four CPVs and a current corrigendum chain.

Key normalization:

- Invitation Reference → solicitation external identifier;
- Ministry / Agency / PE remain separate roles;
- `WD-2` remains Lot Identification, not Tender Package No.;
- blank Project/Programme Code, Project/Programme Name and Tender Package No remain `UNKNOWN`;
- each corrigendum becomes an immutable event/release rather than overwriting history.

Output:

- formal procurement confirmed;
- lifecycle is at least live-solicitation/tender stage;
- official current dates updated from the latest authoritative event;
- no duplicate commercial opportunity created.

### 7. ARGUS — check internal customer intelligence

Only after external procurement state and identity are resolved does ARGUS query authorized Access Asia internal customer intelligence relevant to this buyer/requirement:

- existing ARGUS observations/knowledge linked to Bangladesh Coast Guard or the CPV lineage;
- SharePoint Business Intelligence/opportunity/project records;
- HubSpot buyer/customer relationship context, interactions, notes and deals where authorized;
- prior correspondence, meeting notes, quotations, proposals and concept material;
- supplier/product/installed-base history and previous research.

The purpose is to answer:

- Did Access Asia know about this requirement before tender publication?
- Which Coast Guard/customer relationships or discussions relate to it?
- Have any shipyards/OEMs already been considered or contacted?
- Is there prior technical, budget, project or competitor knowledge?
- Is there an existing Access Asia commercial position that changes the next action?

Internal evidence is used for Access Asia history/relationship claims and corroboration. It is not treated as independent proof of government approval or procurement unless the source itself has that authority.

### 8. ARGUS — reconcile internal and official evidence

ARGUS creates one mission-local picture:

**Known from official evidence**
- Ministry of Home Affairs;
- Bangladesh Coast Guard Force;
- Project Director as PE;
- four CPVs;
- GoB Development Budget;
- ICT One Stage & Two Envelope method;
- eligibility baseline;
- tender security;
- completion period;
- current corrigendum dates.

**Known from internal canonical state**
- the procurement/requirement/solicitation/lot/item lineage already exists;
- publication/corrigendum observations are already part of the case history.

**Still material / potentially unknown**
- upstream official project/programme identity if not independently evidenced;
- exact approved budget/project lineage;
- full technical specification and evaluation conditions from tender documents;
- installed-base and replacement rationale;
- incumbent/likely competitors;
- qualified and willing international shipyards/OEMs;
- Access Asia relationship/positioning history;
- participation path and partner conflicts.

### 9. ARGUS — build the Research Frontier

ARGUS ranks only questions capable of changing the commercial decision.

For a live CPV tender, likely high-value questions are:

1. What full technical and commercial eligibility requirements can disqualify a bidder?
2. Which shipyards/OEMs meet the relevant patrol/combat-vessel references and delivery requirements?
3. Which candidates are export-feasible, commercially available and willing to partner with Access Asia?
4. Does Access Asia already have customer/OEM relationships or conflicting representations relevant to the tender?
5. Which competitors/incumbents are materially likely?
6. Does upstream project/budget intelligence change the pursuit or supplier strategy?

Low-value historical research is deferred when it would not change participation or strategy before the live deadline.

### 10. ARGUS — adaptive 360° collection

ARGUS activates only the branches needed to close the Research Frontier:

- `institution_stakeholders` — if decision-maker/role gaps remain;
- `programme_project` / `budget_funding` — if upstream lineage affects strategy;
- `procurement_acquisition` — full tender/corrigendum/eligibility/evaluation picture;
- `technical_installed_base` — specifications, vessel class, replacement/expansion context;
- `internal_intelligence` — Access Asia position/history;
- `supplier_competitor` — suitable OEM/shipyard universe, references, competitors;
- `ecosystem_influence` — consultants/integrators/partners if material;
- `commercial_participation` — export, JV/local representation, security, delivery, service/support constraints;
- `timing_triggers` — closing dates, extensions and other events.

Independent safe reads may run in parallel after startup dependencies are satisfied. ARGUS does not call ATLAS after every search or newly discovered lead.

### 11. Decision sufficiency

ARGUS stops expanding research when additional collection is unlikely to change:

- existing-vs-new identity;
- current procurement/lifecycle interpretation;
- participation feasibility;
- supplier shortlist/strategy;
- commercial risk;
- next Access Asia action.

The stopping question is **“Can more research materially change the decision?”**, not “Is there anything else we could search?”

### 12. One ARGUS return

ARGUS returns one structured package containing proportionately:

- resolved institutional hierarchy;
- existing/new/ambiguous identity outcome;
- official procurement state;
- internal customer-intelligence summary;
- 360° coverage;
- evidence/provenance;
- Research Frontier and remaining material unknowns;
- supplier/product/competitor assessment where material;
- recommended next action;
- one proposed mutation batch where persistence is useful.

Normal result for this case:

- use existing CPV lineage;
- do not create another opportunity merely because a tender/corrigendum was observed;
- update current source/event/observation state as needed;
- focus remaining research on decision-relevant tender, internal-positioning and supplier/competitor gaps.

### 13. ATLAS verifies and persists once

ATLAS verifies result/handoff correlation, evidence, identity outcome, approval requirements and the proposed mutation batch.

If canonical persistence is authorized:

`fetch latest SharePoint SQLite → verify version/integrity → resolve identity again → apply one local transaction → preserve provenance/mutation log → integrity + FK checks → re-check target → replace same file → verify uploaded state`

ARGUS does not persist every intermediate discovery.

---

## Callback test

The following are **not** ARGUS→ATLAS callback reasons:

- project name is missing;
- budget is unknown;
- one source returns zero results;
- supplier universe has not been built yet;
- another official portal/source should be searched;
- a competitor lead appears;
- a tender document requires deeper extraction.

The following **are** callback/escalation reasons:

- `MATERIAL_SCOPE_CHANGE`;
- `AUTHORIZATION_REQUIRED`;
- `POLICY_OR_SECURITY_CONFLICT`;
- `MATERIAL_AMBIGUITY`, including a probable/unresolved existing-opportunity match where the wrong choice could create or merge the wrong object.

## Architecture result

**PASS — institution-first, identity-aware, one-handoff/one-return design.**

The CPV case validates the intended separation:

- ATLAS compiles, authorizes, verifies and persists;
- ARGUS resolves the institution and canonical identity before broad research;
- official procurement evidence is checked before internal customer intelligence in the deterministic startup;
- ARGUS then performs adaptive 360° research without routine callbacks;
- no new `IntelligenceCase` canonical object is created for mission coordination;
- current mutable state remains in the single SharePoint SQLite registry;
- one underlying opportunity may contain multiple procurement/source events without duplicate opportunity creation.
