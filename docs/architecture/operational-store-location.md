# ARGUS Operational Store Location

The Access Asia production structured operational store is the SharePoint SQLite file:

`General/Business Intelligence/30_OPERATIONS/ARGUS_OPERATIONAL.sqlite`

GitHub contains schema, code, tests and migration logic only. Runtime mutations must fetch the latest SharePoint file, verify it, mutate locally in one transaction, run integrity checks, and replace the same SharePoint file so SharePoint version history remains the recovery mechanism.
