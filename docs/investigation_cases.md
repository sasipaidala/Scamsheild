# Investigation Cases — Milestone 2

## Implemented

- Create a case with a unique `SS-XXXXXXXX` reference, title, priority, description and initial evidence item.
- Persist cases, evidence and activity events in SQLite using schema migration 4.
- Browse and filter cases by status; inspect a case's evidence and activity history.
- Update case status, attach additional evidence, and save analyst notes.
- Export a case record as JSON.
- For URL, domain, IP address and file-hash evidence, perform an exact-match lookup against the locally imported Threat Intelligence IOC inventory and display the source provenance returned by that inventory.

## Data handling

Case evidence is stored locally in the configured SQLite database. Do not submit passwords, OTPs, payment-card information or unrelated personal data. URL evidence is stored as text and is not fetched. No external provider is contacted by case creation or IOC matching.

## Limitations

- Single local workspace; no user accounts, role-based access control, multi-user concurrency workflow or cloud synchronization.
- Case evidence is manually submitted; existing analyzer results are not yet automatically attached as structured artifacts.
- IOC matching is exact-match only. It does not perform DNS resolution, URL crawling, fuzzy matching or live threat-feed lookups.
- JSON export is available; polished PDF reports are a separate Reports milestone.
