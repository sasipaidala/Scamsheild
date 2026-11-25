# Threat Intelligence — IOC Workspace (Milestone 1)

## Scope

This milestone provides local, import-based IOC storage and exact-match lookup. It does not connect to external feeds, make network requests, resolve DNS, open URLs, or independently verify source claims.

## Supported indicator types

- `domain`: fully qualified domain names
- `ip`: IPv4 and IPv6 addresses
- `url`: HTTP and HTTPS URLs without embedded credentials
- `hash`: hexadecimal MD5, SHA-1, SHA-256, and SHA-512 digests

## CSV format

Required columns: `indicator` and `type` (or `indicator_type`). Optional columns: `threat_type`, `confidence` (0–100), `first_seen`, `last_seen`, `expires_at`, and `description`.

Example:

```csv
indicator,type,threat_type,confidence,first_seen,last_seen,expires_at,description
example.com,domain,phishing,70,,,,Example placeholder; replace with an authorized feed record
```

The example is documentation only and is not imported as live intelligence.

## Provenance and interpretation

Each record retains the source name, optional source reference URL, source-supplied confidence and timestamps, description, and import timestamp. The same IOC from different sources is retained as separate evidence. Re-importing the same IOC from the same source updates that source's record.

A match means only that an imported source listed the indicator. A no-match result does not mean safe. Confidence is not calculated by ScamShield. Expiration metadata is stored but not used to declare current validity.

## Limits

- CSV maximum size: 5 MB
- CSV maximum rows: 50,000
- Inventory view: most recent 500 records
- Lookup: exact match after type-specific normalization
- No live feeds, DNS, WHOIS, certificate checks, URL fetching, or malware detonation

Only import data you are authorized to use and redistribute.
