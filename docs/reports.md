# Investigation Reports

The Reports workspace creates point-in-time snapshots from locally stored Investigation Cases.

## Included outputs

- Individual case report in Markdown and JSON.
- Optional inclusion of case activity (notes and status/evidence events).
- Saved report archive stored in SQLite.
- CSV case register containing case metadata and evidence counts, not evidence content.

## Data and limitations

Reports reflect records saved at generation time. Later case edits do not retroactively alter an already generated snapshot. Generate a new report to reflect updates. Reports do not independently verify evidence, establish legal conclusions, or imply that a threat-intelligence indicator proves malicious conduct. External provider lookups are not implied. Review reports and remove unnecessary personal information before sharing.

The report archive is local to the configured SQLite database. It has no multi-user access control, digital signature, tamper-evident audit storage, PDF export, or delivery workflow in this milestone.
