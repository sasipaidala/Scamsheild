# ScamShield AI — Architecture Notes

## Current structure

- `app.py`: Streamlit entry point, configuration, database initialization and theme setup.
- `components/`: shared brand and navigation elements.
- `core/`: environment configuration, theme tokens, dashboard demonstration fixtures and interface-level validation.
- `database/`: local SQLite connection management and versioned migrations; no investigation records are written yet.
- `services/message_service.py`: local, deterministic message-indicator rules and explainable assessment.
- `services/url_service.py`: passive URL parsing and explainable structural indicators; never makes network requests.
- `pages/url_analyzer.py`: UI for passive URL analysis.
- `pages/`: public landing page, workspace overview, intake form, message analyzer and explicitly marked future-module placeholders.
- `tests/`: unit/regression checks for core behavior and message-analysis rules.

## Phase 2 boundaries

The public landing page and dashboard shell are presentation/interface features. Dashboard charts and scores remain synthetic demo fixtures, marked as such and toggleable. They must not be mixed with real account data. Final production metrics must be derived from actual persisted investigation and analysis records.

## Phase 3 boundaries — current

The message analyzer runs local phrase/pattern rules only. It creates findings and a non-probabilistic indicator score with explanations. It does not contact external services or persist submitted content. Initial English, Telugu and Hindi phrase coverage exists, but representative multilingual accuracy validation has not been completed. See `message_detection.md` for the rule scope and limitations.

Passive URL structural analysis is implemented locally; it does not resolve DNS, fetch pages, follow redirects, or check reputation. Phone-number validation/reputation is not implemented yet.

## Next dependencies

1. Implement phone-number normalization and approved provider adapters where credentials and terms permit.
2. Implement case/evidence persistence and user ownership controls.
3. Replace demo dashboard metrics with repository-backed data once real records exist.
4. Add authorized external intelligence integrations, then PDF/JSON reports and production hardening.

External provider adapters must remain optional and must not cause the local analysis path to fail when they are unconfigured or unavailable.
