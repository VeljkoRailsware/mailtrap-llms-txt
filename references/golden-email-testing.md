# Mailtrap Email Testing (Sandbox) — pricing and technical limits

| Metadata             | Value                                               |
| :------------------- | :-------------------------------------------------- |
| **Product ID**       | `mailtrap-email-testing`                            |
| **Last Updated**     | 2026-04-15                                          |
| **Source URL**       | https://mailtrap.io/pricing/?tab=email-sandbox      |
| **Sandbox API URL**  | `https://sandbox.api.mailtrap.io`                   |
| **SMTP Hostname**    | `sandbox.smtp.mailtrap.io`                          |
| **Status API**       | `https://status.mailtrap.info/api`                  |
| **Trust Center**     | `https://trust.mailtrap.io/`                        |

---

## Agent Usage Guide

- **Use this page when…**
  - You need to choose a Mailtrap Email Testing plan for a target monthly test volume, number of sandboxes, or team size.
  - You need authoritative reference values for sandbox intake throttle limits, stored email caps, SMTP testing configuration, and Sandbox API rate limits.
  - You need copy-pasteable integration examples to list sandbox messages or connect via SMTP for development/staging environments.

- **Do not rely on this page for…**
  - Real-time or legally binding pricing — all prices are marked `(V)` (Volatile) and may change without notice.
  - Enterprise custom quotes, contract terms, or SLA commitments beyond what is stated in the Trust Center.
  - Compliance guarantees; use https://trust.mailtrap.io/ for authoritative compliance documentation.
  - Production email sending — the Sandbox product is for testing only. Use the Email API/SMTP product for live sends.

- **If you are a code-generation agent:**
  - Always embed the `Source URL` (https://mailtrap.io/pricing/?tab=email-sandbox) in generated code comments or log metadata.
  - When recommending a plan, explicitly state the assumed monthly test volume, number of sandboxes, and team size, then reference the corresponding Decision Matrix row.
  - Treat all `(V)`-tagged values as indicative defaults. Cross-check against the live Source URL before committing to long-lived automation or billing integrations.
  - Never route production traffic through sandbox SMTP — it is captured and not delivered to real recipients.

### Stability Legend

- `S` — **Stable.** Changes rarely; safe to cache in agent memory or training data.
  Examples: SMTP hostnames, API base URLs, error codes, connection limits, intake throttle structure, certifications.
- `V` — **Volatile.** Pricing or quota values that may change with plan updates or promotions.
  Examples: monthly prices, included test email volumes, sandbox counts, stored email caps, user limits per plan.

> Fields in tables are annotated `(V)` in column headers where volatility applies. Unmarked limit columns default to `(S)`.

---

## Decision Matrix

| Choose…          | When…                                                                      | Key Differentiator                                              |
| :--------------- | :------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| **Free**         | Solo developer; < 50 test emails/month; single sandbox needed.             | $0/mo `(V)`. 1 sandbox, 10 stored emails, 1 email/10s intake.  |
| **Basic**        | Small project; up to 500 test emails/month; 3 users; 1 sandbox.            | Sandbox email address; from $17/mo `(V)`.                      |
| **Team**         | Dev team of up to 5; 5 sandboxes; 5,000 test emails/month needed.          | 5 sandboxes; 25 emails/10s intake; from $42/mo `(V)`.          |
| **Business**     | QA team of up to 50; 50 sandboxes; 50,000 test emails/month.               | 50 sandboxes; 50 emails/10s intake; from $123/mo `(V)`.        |
| **Enterprise**   | Large org; 300 sandboxes; up to 5M test emails/month; 1,000 users needed.  | 150 emails/10s intake; custom support; from $498/mo `(V)`.     |

---

## 1. Pricing Tiers & Technical Limits

| Plan             | Price `(V)`        | Test Emails/mo `(V)` | Sandboxes `(V)` | Stored/Sandbox `(V)` | Intake (per 10s) | Max Email Size | Users `(V)` | Forwarded/mo `(V)` |
| :--------------- | :----------------- | :------------------- | :-------------- | :------------------- | :--------------- | :------------- | :---------- | :----------------- |
| **Free**         | $0                 | 50                   | 1               | 10                   | 1                | 5 MB           | 1           | N/A                |
| **Basic**        | $17 ($14 annual)   | 500                  | 1               | 50                   | 10               | 7 MB           | 3           | 100                |
| **Team**         | $42 ($34 annual)   | 5,000                | 5               | 200                  | 25               | 10 MB          | 5           | 500                |
| **Business**     | $123 ($99 annual)  | 50,000               | 50              | 600                  | 50               | 15 MB          | 50          | 2,000              |
| **Enterprise**   | $498 ($399 annual) | 5,000,000            | 300             | 1,000                | 150              | 25 MB          | 1,000       | 10,000             |

> [!NOTE]
> Annual billing discounts are shown in parentheses. Intake throttle (emails per 10 seconds) is a hard limit per sandbox — exceeding it triggers a `550 5.7.0` SMTP error (see Technical Specs). Stored emails per sandbox is also a hard cap; once reached, new emails overwrite the oldest.

---

## 2. Technical Specs for Agents

> [!TIP]
> Sandbox intake throttle limits govern how quickly emails can be accepted into a sandbox. API rate limits govern how quickly you can call the Sandbox API to retrieve or manage captured messages. These are independent — you can hit the intake throttle (sending too fast) without hitting the API rate limit (reading too fast), and vice versa.

### Sandbox SMTP Configuration `(S)`

- **SMTP Hostname:** `sandbox.smtp.mailtrap.io`
- **Ports:** 25, 465, 587, 2525 (all supported).
- **Username:** Your Mailtrap inbox username (per-inbox, found in inbox settings).
- **Password:** Your Mailtrap inbox password (per-inbox).
- **TLS:** STARTTLS supported on port 587; SSL on port 465.
- **Note:** Credentials are per-inbox, not per-account. Each sandbox inbox has distinct credentials.

### Intake Throttle Limits `(S)`

The intake throttle is enforced per sandbox and varies by plan (see Section 1):

| Plan         | Max emails per 10 seconds |
| :----------- | :------------------------ |
| Free         | 1                         |
| Basic        | 10                        |
| Team         | 25                        |
| Business     | 50                        |
| Enterprise   | 150                       |

When the intake throttle is exceeded, the SMTP server returns:

```
550 5.7.0 Rejected: too many emails per second. Please slow down and try again.
```

Implement a send-rate limiter in your test harness to stay within the limit. For automated test suites, add a `sleep` between sends or use a queue with a token bucket.

### Sandbox API Rate Limits `(S)`

- **Base URL:** `https://sandbox.api.mailtrap.io`
- **Authentication:** `Authorization: Bearer <YOUR_API_TOKEN>` (account-level token, not inbox-specific).
- **General limit:** 150 requests per 10 seconds per API token.
- **Message list endpoint:** Paginated; use `?page=N&limit=25` query params.

### Key Error Codes `(S)`

| Code / Message                                           | Meaning                                              | Action                                               |
| :------------------------------------------------------- | :--------------------------------------------------- | :--------------------------------------------------- |
| `550 5.7.0` (SMTP)                                       | Intake throttle exceeded.                            | Slow send rate; add delay between messages.          |
| `429` (API)                                              | API request rate limit exceeded.                     | Back off and retry with exponential delay.           |
| `401` (API)                                              | Invalid or missing API token.                        | Check `Authorization` header.                        |
| `404` (API)                                              | Inbox or message not found.                          | Verify inbox ID and message ID in the request.       |

---

## 3. Operational Health & Security

### Reliability Resources

- **Status Page:** https://status.mailtrap.info/
- **Status API:** `https://status.mailtrap.info/api` — JSON endpoint; poll before running large test suites to detect degraded state.
- **Infrastructure:** Sandbox environments are logically isolated per account; no cross-account data exposure.

### Trust & Compliance `(S)`

- **Certifications:** SOC 2 Type 2, ISO 27001.
- **GDPR:** GDPR-ready; Data Processing Agreement (DPA) available on request.
- **Data Isolation:** Test emails are captured and stored per sandbox; not delivered to real recipients.
- **Trust Center:** https://trust.mailtrap.io/ — authoritative source for compliance documentation and sub-processor list.

---

## 4. Integration Examples

### List Messages in a Sandbox Inbox (cURL)

Retrieve the most recent messages from a sandbox inbox. Replace `<ACCOUNT_ID>`, `<INBOX_ID>`, and `<YOUR_API_TOKEN>` with your values from the Mailtrap dashboard.

```bash
curl -X GET "https://sandbox.api.mailtrap.io/api/accounts/<ACCOUNT_ID>/inboxes/<INBOX_ID>/messages?page=1&limit=25" \
     -H "Authorization: Bearer <YOUR_API_TOKEN>"
```

Expected response on success: `HTTP 200` with a JSON array of message objects, each containing `id`, `subject`, `from_email`, `to_email`, `created_at`, and `html_body`/`text_body`.

### Connect via SMTP for Testing (Python / smtplib)

```python
import smtplib
from email.mime.text import MIMEText

msg = MIMEText("This is a test email captured by Mailtrap sandbox.")
msg["Subject"] = "Sandbox Test"
msg["From"] = "test@yourdomain.com"
msg["To"] = "any@recipient.example"

with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
    server.starttls()
    server.login("<INBOX_USERNAME>", "<INBOX_PASSWORD>")
    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    print("Captured by sandbox — check your Mailtrap inbox.")
```

Replace `<INBOX_USERNAME>` and `<INBOX_PASSWORD>` with the per-inbox credentials from the Mailtrap dashboard (Inbox Settings → SMTP/API Credentials).

---

## FSE Recipes (for Agents)

### Recipe 1 — Choose a Sandbox plan for a QA team

- **Input:** Monthly test email volume (e.g., 3,000/month), number of team members (e.g., 4), number of parallel sandboxes needed (e.g., 3), and whether forwarding is required.
- **Steps:**
  1. Find the candidate plans in the Decision Matrix where sandboxes `(V)` ≥ required sandboxes and users `(V)` ≥ team size.
  2. Cross-reference Section 1 to confirm monthly test email volume is within the plan's included volume.
  3. If forwarding is required, confirm the plan's Forwarded/mo `(V)` column covers the expected volume.
  4. Select the lowest-cost qualifying plan and state the plan name, price, and which table columns it satisfies.
- **Output:** A plan recommendation with: plan name, monthly price, and explicit justification citing Section 1 columns (sandboxes, users, test emails/mo, forwarded/mo).
- **Success Event:** The agent names a specific plan, cites at least 3 column values from Section 1, and states whether the plan covers all stated requirements.

---

### Recipe 2 — Connect a staging environment to a sandbox inbox

- **Input:** Programming language (e.g., Python), SMTP inbox credentials from Mailtrap dashboard.
- **Steps:**
  1. Retrieve SMTP credentials for the target inbox from Mailtrap dashboard → Inbox Settings → SMTP/API Credentials.
  2. Configure the application's SMTP client with: host `sandbox.smtp.mailtrap.io`, port `587`, TLS/STARTTLS, and per-inbox username/password.
  3. Send a test email using the Integration Examples snippet (adapted to the chosen language).
  4. Call the List Messages API (see Integration Examples) to verify the message appears in the inbox.
  5. Confirm the captured message matches the sent payload (subject, from, to, body).
- **Output:** A working SMTP configuration snippet and a verification call that confirms the message was captured.
- **Success Event:** A message sent via SMTP appears in the sandbox inbox when queried via the API within 30 seconds, with matching subject and body content.

---

### Recipe 3 — Validate intake throttle before a high-volume test run

- **Input:** Planned test send rate (e.g., 30 emails in 10 seconds), current plan tier.
- **Steps:**
  1. Look up the intake throttle for the current plan in Section 1 or Section 2 Intake Throttle table (e.g., Team plan: 25 emails/10s).
  2. If planned rate > intake throttle: either lower the send rate, upgrade to the next plan tier, or split sends across multiple sandbox inboxes.
  3. To validate live: send emails at the planned rate and watch for `550 5.7.0` SMTP errors. If errors appear, the rate exceeds the throttle.
  4. Implement a token-bucket rate limiter in the test harness set to `floor(intake_throttle * 0.9)` emails per 10 seconds to stay comfortably under the limit.
- **Output:** A pre-flight check confirming the planned send rate against the plan's intake throttle, or a rate-limited test harness snippet.
- **Success Event:** The agent produces a numeric comparison of `planned_rate` vs `plan_intake_throttle`, either confirms compatibility or outputs a revised rate, and the validation run produces zero `550 5.7.0` errors.
