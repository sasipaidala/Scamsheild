# ScamShield AI

**Detect the Signal. Stop the Scam.**

ScamShield AI is being built incrementally as a transparent, evidence-led digital scam investigation platform.

## Current milestone: Phase 3 — local message and passive URL analysis

Implemented:
- Dark and light themes with shared design tokens.
- Branded, responsive Streamlit application shell and sidebar navigation.
- Public Home page with product introduction, feature overview, workflow and trust disclosures.
- Dashboard/Overview with KPI cards, activity trend, risk distribution, category bars, score ring and recent sample records.
- Every dashboard number and chart is prominently marked as synthetic demonstration data; a toggle switches to the true empty workspace state. Demo fixtures are allowed only when `SCAMSHIELD_ENV=development`; they are automatically disabled in test and production environments.
- Expanded theme tokens and explicit light/dark styling for widget labels, inputs, dropdowns, popovers, buttons, tabs, alerts and navigation.
- Interactive investigation intake form for message, URL and phone-number input types.
- Local message analyzer with explicit, versioned heuristic rules for OTP/credential requests, advance fees, account pressure, payment requests, unrealistic offers, recruitment approaches, urgency and off-platform migration.
- Passive URL structure analyzer for HTTP/HTTPS parsing, user-info syntax, IP-literal hosts, punycode, known shorteners, long/multi-label hostnames and non-standard ports. It never resolves or fetches a URL.
- Message findings include matched excerpts, explanations, rule weights, a non-probabilistic indicator score, safe next steps and limitations.
- Initial phrase coverage for English, Telugu and Hindi, without claims of validated multilingual accuracy.
- Message analysis runs locally with no external requests and is not persisted; results are retained only in the active Streamlit session.
- Quick investigation launcher on the public Home page.
- Thirteen unique destinations: public Home at `/`, Overview at `/overview`, plus the remaining workspace destinations.
- Theme selection retained in the URL/session.
- Local SQLite schema initialization and configuration.
- Automated tests for routes, theme, configuration, database setup, interface validation and the first local message rules.

Not implemented yet:
- Phone-number validation/reputation checks. URL analysis is structural only and is not reputation or malware detection.
- Production validation of message detection across a representative dataset and all supported languages.
- External threat-intelligence integrations.
- Authentication, password reset, user-owned cases or persistent case management.
- Live dashboard metrics or report exports. The current charts and scores are interface-preview fixtures, not live analytics.
- Full English/Telugu/Hindi interface localization.
- Screenshot OCR and AI-assisted investigation.

The message analyzer performs local heuristic checks only. Its score is not a statistical probability or definitive determination. A result with no matching rules does not prove a message is safe. Phone inputs still receive only basic presence/size checks. URL inputs receive passive structural checks only. No evidence is saved to the database or sent to third-party providers. Streamlit may retain field values and the latest message result in the active session until the session ends or is reset.

## Requirements

- Python 3.10 or newer
- pip

## Local setup — Windows PowerShell

```powershell
cd scamshield-ai
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pytest
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

These commands use the virtual-environment Python directly and do not require PowerShell script activation.

## Local setup — macOS / Linux

```bash
cd scamshield-ai
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m pytest -q
streamlit run app.py
```

The local SQLite database is initialized automatically at `data/scamshield.db`. The `data/` folder is ignored by Git.

## Tests

```bash
python -m pytest -q
```

The test suite verifies route uniqueness, configuration validation, database initialization, theme behavior, dashboard demo-fixture boundaries, interface-level input checks and message-rule behavior. It does not prove browser responsiveness or production detection accuracy.

## Theme behavior

Use the sidebar selector to switch between dark and light themes. Shared color tokens style Streamlit labels, form controls, dropdowns, buttons, popovers, alerts and navigation as well as custom dashboard components. The selected theme is reflected in the URL and Streamlit session; account-level preference storage is not implemented.

The current visual system uses a graphite-and-deep-teal dark palette and a separately tuned cool-white light palette. A CSS-only ambient black-hole scene (slow accretion-disc rotation and drifting stars) sits behind the interface. It does not intercept clicks, is subdued in light mode, and stops animating when the operating system requests reduced motion. No extra JavaScript or WebGL dependency is required for this theme update. Verify both themes in your local browser because automated tests do not prove visual browser rendering.

## Security notes

- Do not add API keys, passwords or real investigation data to source files.
- `.env` and Streamlit secrets are excluded from Git.
- Message analysis uses local rules only; it does not fetch URLs or call external providers.
- Phone tools do not yet perform number analysis or reputation checks. URL analysis is passive and structural only.
- No evidence, analysis result or case data is written to the application database in the current message-analysis milestone.
- SQLite is for local development; production hosting and durable database storage require a later backend/deployment decision.
- The project makes no claim of regulatory compliance, penetration-test certification or production security review.

## Milestone discipline

Build, test and verify one milestone at a time. URL and phone analyzers, persistence, case management and authorized provider integrations must be implemented and tested before the app presents account-level live metrics or external intelligence. Demo dashboard data remains synthetic and separate from real application records.

## Message analyzer details

See [`docs/message_detection.md`](docs/message_detection.md) for the rule families, indicator scoring, limitations and production-validation requirements.

## Neon interface update

The interface uses an electric-cyan / violet accent system with restrained glow states, card hover feedback, animated content entry, and a reduced-motion fallback. The URL Analyzer includes clickable local examples for exploring structural findings. Sample links are parsed as text only; the app does not open or fetch them. The visual theme does not change the meaning of analysis results or turn structural indicators into a safety verdict.


## Cinematic landing experience

The public landing page now opens with a self-contained, scroll-driven canvas scene. Scrolling moves through three narrative stages: a contained signal, evidence mapping, and defense readiness. The scene uses a dark cinematic palette with restrained green accents and a subtle grid; the previous galaxy/black-hole background has been removed. The scene is locally rendered with Canvas 2D (no image assets or external JavaScript CDN required) and respects reduced-motion preferences. The rest of the application retains native Streamlit navigation and investigation pages.


## Optional external phone intelligence (OpenTrust)

ScamShield can query OpenTrust's India-focused merchant-community phone reports.
Access is not automatic: register a business/merchant account with OpenTrust,
wait for admin approval, then create an API key in its dashboard. The provider
currently advertises 100,000 free checks for approved accounts; limits and
eligibility are controlled by OpenTrust.

Set `OPENTRUST_API_KEY` in the project's local `.env` file (never commit that
file). ScamShield hashes the normalized `+91` number with SHA-256 before sending
it to OpenTrust, following its documented `phone_sha256` / `phone_length` API.
OpenTrust reports are merchant-submitted observations, not verified findings.
A zero report count means no matching reports were found in that provider, not
that the number is safe. Without a key, the external provider remains unconfigured
and the local ScamShield community lookup continues to work.

Provider setup: https://opentrust.in/faq and https://opentrust.in/docs

## Email Spam Analysis

The Message Analyzer now includes an **Email Spam Analysis** mode. It reviews supplied sender/display-name/Reply-To fields, subject and body, extracts embedded URLs without opening them, and can parse SPF/DKIM/DMARC status strings from a user-supplied `Authentication-Results` header. All checks are local heuristics; header values are not independently verified, and no DNS, URL reputation, attachment, or external provider checks are performed. A result with no configured indicators is not a safety guarantee. Email content is not persisted by this analyzer.

## Investigation Cases (Milestone 2)

The Investigation Cases workspace now supports persistent local case records, evidence attachments, analyst notes, status history and JSON export. URL, domain, IP and file-hash evidence can be checked against the locally imported Threat Intelligence inventory using exact-match lookup. This is not a live provider lookup and a missing match is not a safe verdict. See `docs/investigation_cases.md` for scope and limitations.

## Security Awareness and Help & Support

The Security Awareness page contains five educational modules with knowledge checks and locally persisted scores. The Help & Support page provides searchable FAQs, troubleshooting guidance, and a local SQLite-backed support request register. Support tickets are **not emailed or sent to a staffed support queue** in this release. See `docs/security_awareness.md` for scope and data-handling notes.
