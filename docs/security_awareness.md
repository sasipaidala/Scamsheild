# Security Awareness

The Security Awareness page provides five short, practical lessons: phishing and suspicious links; OTPs, passwords and account security; fake jobs and recruitment scams; payment and UPI fraud; and impersonation/social engineering. Each lesson has a knowledge check. Quiz scores are stored locally in SQLite. A topic is counted as completed only after a 100% score; attempts can be repeated.

Content is educational guidance, not a guarantee that any message, person, URL or transaction is safe. The emergency guidance is India-oriented and points users to their bank/payment provider, 1930 and cybercrime.gov.in.

# Help & Support

The Help page contains searchable FAQs and troubleshooting notes, plus a local support-request form. Tickets are persisted in SQLite and receive a reference such as `SS-HELP-XXXXXX`. The current release does not send email, notify a support team, expose a hosted ticket queue, or promise a response SLA. Only ticket metadata is shown in the recent-request table; ticket descriptions are not exposed there.

Do not submit passwords, OTPs, API keys, access tokens, full payment-card/account numbers or unrelated personal information. Back up the configured SQLite database securely and restrict local filesystem access.

## Database migration

Schema migration 6 adds `awareness_progress` and `support_tickets`. Existing tables and records are preserved.
