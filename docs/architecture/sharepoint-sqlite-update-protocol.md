# SharePoint SQLite Update Protocol

1. Resolve the exact SharePoint file target and read its current metadata/version.
2. Download the current `ARGUS_OPERATIONAL.sqlite` to local working storage.
3. Run SQLite integrity and foreign-key checks before mutation.
4. Resolve canonical identity before creating a new object; never deduplicate by title alone.
5. Apply one serial transaction under ATLAS write authorization.
6. Record the mutation in the database mutation log.
7. Run integrity and foreign-key checks again.
8. Re-read the SharePoint file metadata before replacement to reduce stale-write risk.
9. Replace the same SharePoint file, not a new routine copy.
10. Verify the uploaded file and retain SharePoint version history for rollback.

The database must never be opened directly as a network SQLite database from SharePoint. It is always downloaded, changed locally, verified, and replaced.
