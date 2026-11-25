# Message detection — initial local ruleset

**Implementation status:** first local analysis module implemented; not production-validated.

## Processing flow

1. Validate that the input is text, non-empty and no longer than 5,000 characters.
2. Normalize Unicode with NFKC, remove zero-width formatting characters and collapse whitespace.
3. Run deterministic regular-expression rules locally.
4. Produce findings with a rule ID, matched excerpt, severity label, rule weight and plain-language explanation.
5. Calculate an uncalibrated indicator score from the rule weights and documented combinations.
6. Return precautions, observations, rule-set version, timestamp and limitations.

The analysis service performs no outbound network requests and does not persist the submitted content. The Streamlit page keeps the current result in the active session only.

## Initial rule families

- Requests for OTPs, passwords, PINs, CVVs or verification codes.
- Advance, registration, processing, training, interview or joining fees.
- Account restriction or KYC pressure.
- Direct requests to pay or transfer money.
- Unusually attractive job, income or investment promises.
- Job/recruitment approaches.
- Urgency or consequence pressure.
- Requests to move a conversation to another messaging platform.

Initial English, Telugu and Hindi phrase patterns are included. This does **not** mean broad multilingual accuracy has been established. Mixed-language expressions, spelling variation, transliteration, regional phrasing, sarcasm, context, quoted text and adversarial obfuscation can be missed or misinterpreted.

## Indicator score

The displayed score is a transparent heuristic sum, capped at 100. It is not a statistical probability, calibrated risk estimate or verdict. The rules add small contextual bonuses for combinations such as:

- credential request + urgency pressure;
- advance fee + job offer;
- account restriction + credential or payment request.

A single common word is not intended to trigger a high assessment. A protective-context filter suppresses common English advice such as “Never share your OTP”, but this filter is not comprehensive across languages or complex quotations.

## Result meanings

- **Insufficient evidence:** input is too short to support a useful review.
- **No significant indicators detected:** none of the configured rules matched; this does not establish safety.
- **Low / Moderate / High / Critical:** heuristic tiers based on the indicator score, not proof of wrongdoing.

The result includes the matched excerpts and explanations so that a user can inspect why a rule fired.

## Out of scope for this module

- URL destination or reputation validation. A URL found in a message is reported only as an observation.
- Phone number ownership, identity, carrier or reputation lookup.
- External threat-intelligence provider lookups.
- AI interpretation or translation.
- Persistent case/evidence storage, user accounts or report export.
- Calibrated probability or measured detector accuracy.

## Validation required before production

Build a representative, consented and appropriately anonymized dataset; label it with a documented review process; measure false-positive and false-negative rates per language and category; review biases and drift; and tune thresholds against the evaluation set. Do not market a detection accuracy percentage until such validation has been performed.
