# Access Asia Canonical Commercial Graph v1

## Decision

Access Asia uses one canonical commercial graph for shared business reporting across Marketing, Sales, Business Development, Operations, Finance and Management.

The governing principle is:

> Enter a fact once, identify it once, relate it once, and let every department derive its own report from the same canonical commercial graph.

Department-specific databases are prohibited. Department dashboards, reports and analytical marts are derived views over the same canonical identities, facts and relationships.

## System ownership

- **ARGUS SharePoint SQLite** owns the current mutable canonical commercial graph: organizations, material people, products, government projects, requirements, procurement/tenders, opportunities, bids, awards, Access Asia projects, structured contract facts, structured financial facts, relationships, events, observations and provenance.
- **HubSpot** owns Access Asia relationship state, contactability/contact details, emails, calls, meetings, notes, CRM deal workflow, tasks and follow-up. It mirrors ARGUS identities when an organization/person becomes commercially engaged.
- **SharePoint files** own source documents and working files: tender documents, customer intelligence files, proposals, bid packages, contracts, project files, invoices, receipts and other financial evidence.
- **ARGUS GitHub** owns schemas, identity rules, commercial-data rules, migration logic, tests and versioned release baselines.
- **ATLAS GitHub** owns routing, approvals, persistence policy and execution governance.

Cross-system linking uses stable canonical keys and runtime resolution. Native HubSpot IDs, SharePoint item IDs, tokens and personal contact data must never be committed to public Git.

## Identity model

One real-world object receives one canonical identity.

Examples:

- Bangladesh Coast Guard is one `ORGANIZATION` even when it acts as customer, buyer, end user, procuring entity or implementing agency.
- A shipyard is one `ORGANIZATION` even when it acts as OEM, supplier, principal, contractor, partner or competitor.
- Government projects remain `PROJECT` objects.
- Access Asia delivery projects are `ACCESS_ASIA_PROJECT` objects and are never collapsed into government projects.

Roles are contextual relationships/attributes, not duplicate identity universes.

## Commercial lineage

The permanent Access Asia commercial lineage key is the PX ID assigned by ATLAS.

```text
ARGUS opportunity
      ↓ PROMOTE_TO_PX
YYYY_PXNNNNN_SHORTNAME
      ↓
Opportunity
      ↓
Bid
      ↓
Award
      ↓
Access Asia Project
```

The PX ID remains immutable across submission, award, project execution and SharePoint folder moves.

Child objects remain independently addressable:

- `BID-PXNNNNN-NN`
- `AWD-PXNNNNN-NN`
- `AAPJ-PXNNNNN`

A tender does not equal an opportunity. A bid does not replace an opportunity. An award does not replace a bid. An Access Asia project does not replace or redefine the external government project.

## Fact and evidence model

A material fact is recorded once with provenance and history.

Every material fact should be traceable to:

- a source record or authorized internal source;
- observed/recorded time;
- claim state/confidence where applicable;
- the canonical object(s) it describes.

Conflicting observations are retained rather than silently overwritten. The current canonical assessment is derived from the observation/event history.

Example:

```text
OBS-1: project estimate = USD 80m (customer meeting)
OBS-2: official project cost = USD 72m (government document)
```

Both remain available. The system may classify the difference as conflict, scope difference or stale information, but it does not destroy either supported observation.

## Value semantics

Never collapse materially different commercial amounts into a generic `value` field.

Keep distinct fields/facts for:

- government project value;
- procurement estimated value;
- tender value;
- bid value;
- evaluated value;
- award value;
- contract value;
- Access Asia revenue value;
- commission value;
- expected margin;
- actual margin;
- invoiced value;
- collected value;
- direct cost;
- cash exposure.

Each financial fact carries currency and a value type, and should carry PX/project/contract references when attributable.

## Reporting model

The canonical graph is the source. Department outputs are derived analytical views.

### Marketing

Typical dimensions and metrics: sector, product family, buyer, opportunity origin, proactive discovery, campaign/market source, OEM relationship yield and market demand.

### Sales

Typical grain: PX opportunity. Metrics include pipeline value, weighted pipeline, stage, probability, expected award/close, sales cycle and win rate.

### Business Development

Typical grain: requirement/project/opportunity. Metrics include early-stage pipeline, pre-tender detection, funding visibility, supplier coverage and positioning status.

### Operations

Typical grain: Access Asia project. Metrics include milestones, delivery, supplier obligations, customer obligations, issues, acceptance and warranty.

### Finance

Typical grain: financial fact by PX/project/contract. Metrics include contract value, expected revenue, invoiced/collected revenue, commission receivable/received, cost, margin, receivables and cash exposure.

### Management

Portfolio views combine the same canonical facts for pipeline, bookings, revenue, margin, cash, win rate, sector/customer/principal concentration and other executive KPIs.

## Reporting implementation pattern

A star-schema-like reporting layer may expose derived views such as:

- `FACT_OPPORTUNITY`
- `FACT_BID`
- `FACT_AWARD`
- `FACT_PROJECT`
- `FACT_PROCUREMENT`
- `FACT_REVENUE`
- `FACT_COST`
- `FACT_ACTIVITY`

with dimensions such as:

- `DIM_ORGANIZATION`
- `DIM_PRODUCT`
- `DIM_SECTOR`
- `DIM_GEOGRAPHY`
- `DIM_TIME`
- `DIM_FUNDING_SOURCE`

These are read/reporting views, not new master databases.

## Migration rule

This standard does not mutate the live SharePoint SQLite database by itself. The active store remains:

`General/Business Intelligence/30_OPERATIONS/ARGUS_Master_Registry.sqlite`

Before operational activation of new object/fact tables, ARGUS must provide a backward-compatible SQLite migration, regression fixtures, integrity/foreign-key checks and a rehearsal proving no material information loss. ATLAS remains the only write-authority for the production store.
