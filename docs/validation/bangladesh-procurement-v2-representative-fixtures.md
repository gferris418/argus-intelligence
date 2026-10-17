# Bangladesh Procurement v2 — Representative Fixture Validation

**Document ID:** ARGUS-BD-PROC-V2-VAL-001  
**Date:** 2026-10-18  
**Candidate standard:** `profiles/bangladesh-canonical-procurement-standard-v2.0.yaml`  
**Active production/write standard:** v1.3  
**Live registry mutation: false**

## Decision

**GO / NO-GO:** **GO** to the next design gate — define and test the formal v2 JSON Schema / registry write contract and fold the validation addendum into the candidate standard. **NO-GO** for live-record migration or changing the active Bangladesh write authority from v1.3 at this stage.

The representative-fixture exercise found **Material information loss: 0** across the four selected cases. The candidate structure can preserve the decision-relevant and source-supported procurement facts while removing duplicated storage and making previously conflated concepts explicit.

**Semantic equivalence: PASS**  
**Information preservation: PASS**

This result does not mean every historical record can yet be automatically migrated. It means the candidate model successfully represents these materially different procurement patterns without dropping supported facts. Ambiguous legacy fields must still follow the v1-to-v2 migration controls, including deprecation where semantics cannot be resolved safely.

## Fixtures tested

### 1. BCG CPV

Source/current record: `data/registry/current/PROC-BCG-LT001.json`.

Validated preservation:

- tender/invitation reference remains a typed process identifier;
- Ministry of Home Affairs, Project Director PE and Bangladesh Coast Guard roles become `party_role_links` rather than repeated organization strings;
- project context remains linked to `PRJ-BCG-CPV-WD2`;
- procurement category, international competition scope and one-stage/two-envelope configuration remain separate concepts;
- Lot No. `1` and Lot Identification `WD-2` remain distinct;
- quantity 4 vessels is represented as an item quantity;
- BDT 100,000 tender-document fee and BDT 230,000,000 tender security are preserved as typed fee/security objects;
- original and current sale, submission and opening dates are retained in milestone history;
- both deadline extensions remain append-only events;
- `extension_count` is removed as duplicate authoritative state and is derivable as the count of deadline-extension events;
- public experience eligibility, material unknowns and research frontier are preserved.

**Material information loss: 0.**

### 2. DAE Low Lift Pump

Source/current record: `data/registry/current/PROC-DAE-1318662.json`.

Validated preservation:

- e-GP system Tender/Proposal ID `1318662`, PE Invitation Reference `12.01.0000.981.07.005.26-143`, APP ID `229930` and Package No. `GD/DAE/CHAR-28` remain separate typed identifiers;
- Project Code `224385000` stays on linked PROJECT context rather than being duplicated as a procurement identity;
- underlying requirement `REQ-DAE-224385000-CHAR28-LLP` is preserved;
- Goods, OTM and NCT are separated into category `GOODS`, normalized method `OPEN` with source code `OTM`, and competition scope `NATIONAL`;
- envelope/stage configuration is **not inferred** because the source record does not establish it;
- Development budget and Government financing remain distinct concepts;
- Lot `01`, Low Lift Pump description and Project Area location are preserved;
- sale, security, submission, opening, validity, security-validity, tentative delivery/start and completion dates are represented as typed milestones;
- BDT 5,000 tender-document fee and BDT 3,900,000 tender security are preserved;
- raw eligibility `As per TDS` is retained without inventing qualification detail.

**Material information loss: 0.**

### 3. DGDP RHIB

Source/current record: `data/registry/current/PROC-DGDP-248-07-076-26.json`.

Validated preservation:

- DGDP Tender No. `248.07.076.26` remains a typed DGDP process identifier;
- Bangladesh route `BD-DEF-DGDP` is preserved;
- Ministry of Defence, DGDP and Bangladesh Navy become party-role links;
- Navy Wing / NP-8 is represented as the DGDP procurement-unit label rather than another duplicated organization name;
- the item remains RHIB with twin engine, quantity 3 Nos;
- selling start/end, submission deadline and opening are preserved as milestones;
- DGDP enlistment becomes a typed mandatory `ENLISTMENT` requirement while preserving the source wording;
- BDT 5,000 non-refundable schedule purchase charge is preserved as a typed fee;
- the foreign-currency tender basis remains a source observation;
- **foreign-currency basis does not automatically create an INTERNATIONAL competition-scope value**, because the source evidence does not establish that equivalence;
- technical-specification status, supplier-discovery state, material unknowns and Research Frontier remain preserved.

**Material information loss: 0.**

### 4. World Bank SITA PMIPSD/G-01

Source basis: official World Bank disclosed procurement-plan snapshot for project `P506691`, revised 2026-03-06. The representative activity is `PMIPSD/G-01`, described as enhancement, operation and maintenance of the existing BPPA e-GP Data Centre, AMC and supply of new hardware.

Validated preservation:

- procurement activity reference `PMIPSD/G-01` remains a typed procurement identifier;
- World Bank Project ID `P506691` is held in linked PROJECT context and is not duplicated as a procurement-process identifier;
- financing reference `IDA / 78280` is represented as a credit/financing entry rather than being conflated with project or tender identity;
- Goods, Request for Bids, Open-International, Single Stage-Two Envelope and Prior Review remain five distinct source/procurement controls;
- estimated value USD 3,333,333 and source status `Pending Implementation` are preserved;
- planned document-readiness, expected publication, submission/opening, evaluation-completion, contract-signing and completion dates remain distinct planned milestones;
- because this is a procurement-plan snapshot, there is **no fabricated tender notice** in `notices[]`;
- the historical snapshot is explicitly marked stale for current-state purposes, and ARGUS intelligence directs reconciliation to the latest official plan before commercial action.

**Material information loss: 0.**

## Candidate-model improvements discovered by validation

The World Bank planning fixture exposed two missing lifecycle concepts in the initial v2 candidate. They are documented in `profiles/bangladesh-canonical-procurement-standard-v2.0-validation-addendum.yaml`:

1. `PROCUREMENT_DOCUMENT_READY` — planned/actual readiness of bidding/procurement documents or justification. It does not mean the documents were publicly issued.
2. `EXPECTED_PUBLICATION` — planned advertisement/invitation date. It is not the same as an actual published notice.

These additions reinforce the v2 rule that a **milestone is not a notice**. When an actual notice is subsequently published, the planned milestone remains historical planning evidence and the actual publication is added separately.

## Information-preservation matrix

| Case | Identity | Parties/roles | Process controls | Lots/items | Dates/history | Commercial obligations | Evidence/intelligence | Material loss |
|---|---|---|---|---|---|---|---|---:|
| BCG CPV | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 0 |
| DAE Low Lift Pump | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 0 |
| DGDP RHIB | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 0 |
| World Bank SITA PMIPSD/G-01 | PASS | PASS | PASS | PASS | PASS | N/A in plan snapshot | PASS | 0 |

## Non-lossy semantic changes

The following changes deliberately alter **storage location or representation**, not meaning:

- repeated institution names → canonical ENTITY references + typed roles;
- Project IDs/names/costs → linked PROJECT context;
- system ID / tender reference / APP / package / activity reference → typed identifiers;
- NCT/ICT → competition scope rather than procurement method;
- OTM/RFB/etc. → source method plus normalized method;
- stage/envelope wording → process configuration;
- sale/closing/opening/validity dates → typed milestones;
- corrigenda/extensions → events changing milestones;
- extension counters → derived values, not independent facts;
- eligibility/enlistment/experience/etc. → typed requirements;
- document/schedule charges → fees;
- tender/performance guarantees → securities;
- raw source labels/values → observations/provenance.

## Migration safety conclusion

The fixture gate demonstrates that v2 can express the selected Bangladesh e-GP/BPPA, defence/DGDP and World Bank planning patterns without material information loss. It also demonstrated why v2 should remain a candidate until a formal write contract exists.

### GO

Proceed to:

1. fold the validation addendum into the v2 candidate standard;
2. define a machine-validating v2 JSON Schema / registry write contract;
3. validate sparse/unknown handling, typed identifiers, role references and event/milestone constraints at schema level;
4. dry-run the schema against these fixtures and the remaining current procurement records;
5. only then prepare a governed live migration plan.

### NO-GO

Do **not** yet:

- rewrite `data/registry/current/*.json` into v2;
- change the manifest's active Bangladesh procurement standard;
- delete v1.3 compatibility fields;
- infer values to satisfy v2 completeness;
- treat the historical World Bank plan snapshot as current procurement status.

**v1.3 remains active.**
