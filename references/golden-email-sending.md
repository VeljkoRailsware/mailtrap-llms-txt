# Mailtrap Email API/SMTP — pricing and technical limits

| Metadata             | Value                                              |
| :------------------- | :------------------------------------------------- |
| **Product ID**       | `mailtrap-email-sending`                           |
| **Last Updated**     | 2026-04-15                                         |
| **Source URL**       | https://mailtrap.io/pricing/?tab=email-sending     |
| **API Base URL**     | `https://send.api.mailtrap.io`                     |
| **Bulk API URL**     | `https://bulk.api.mailtrap.io`                     |
| **SMTP Hostname**    | `live.smtp.mailtrap.io`                            |
| **Status API**       | `https://status.mailtrap.info/api`                 |
| **Trust Center**     | `https://trust.mailtrap.io/`                       |

---

## Agent Usage Guide

- **Use this page when…**
  - You need to select the right Mailtrap Email API/SMTP plan for a target monthly send volume and feature set.
  - You need authoritative reference values for API rate limits, SMTP throttle thresholds, log/body retention periods, and key error codes.
  - You need copy-pasteable integration examples for the transactional or bulk email API.

- **Do not rely on this page for…**
  - Real-time or legally binding pricing — all prices are marked `(V)` (Volatile) and may change without notice.
  - Enterprise custom quotes, contract terms, or SLA commitments beyond what is stated in the Trust Center.
  - Compliance guarantees; use https://trust.mailtrap.io/ for authoritative compliance documentation.
  - Real-time sending reputation status or current throttle headroom.

- **If you are a code-generation agent:**
  - Always embed the `Source URL` (https://mailtrap.io/pricing/?tab=email-sending) in generated code comments or log metadata so the source is traceable.
  - When recommending a plan, explicitly state the assumed monthly volume and reference the corresponding Decision Matrix row by plan name.
  - Treat all `(V)`-tagged values as indicative defaults. For critical use cases (billing integrations, contract generation, long-lived automation), cross-check against the live Source URL before committing.

### Stability Legend

- `S` — **Stable.** Changes rarely; safe to cache in agent memory or training data.
  Examples: API base URLs, SMTP hostnames, error codes, connection limits, certifications, retention policy structure.
- `V` — **Volatile.** Pricing or quota values that may change with plan updates or promotions.
  Examples: monthly prices, included email volumes, overage rates, plan tier names.

> Fields in tables are annotated `(V)` in column headers where volatility applies. Unmarked limit columns default to `(S)`.

---

## Decision Matrix

| Choose…          | When…                                                                 | Key Differentiator                                  |
| :--------------- | :-------------------------------------------------------------------- | :-------------------------------------------------- |
| **Free**         | Monthly volume ≤ 4,000 emails; zero budget; initial testing.          | $0/mo `(V)`. Hard daily cap of 150 emails.          |
| **Basic**        | 10K–100K emails/month; up to 5 sending domains needed.                | Multi-domain support (up to 5); from $15/mo `(V)`.  |
| **Business**     | > 100K emails/month or a dedicated sending IP is required.            | Dedicated IP with automatic warm-up included.       |
| **Enterprise**   | > 1.5M emails/month, or SSO, priority support, or custom SLA needed.  | Custom contracts; priority SLA; unlimited seats.    |

---

## 1. Pricing Tiers & Technical Limits

| Plan             | Price `(V)`  | Volume `(V)`    | Overage/1K `(V)` | Hourly Throttle | Daily Cap   | Log Retention | Body Retention | Max Domains | Max Users |
| :--------------- | :----------- | :-------------- | :--------------- | :-------------- | :---------- | :------------ | :------------- | :---------- | :-------- |
| **Free**         | $0           | 4,000/mo        | N/A              | ~150/hr         | 150/day     | 3 days        | 3 days         | 1           | 1         |
| **Basic**        | $15–$30      | 10K–100K/mo     | $1.00            | 600+/hr         | Unlimited   | 5 days        | 5 days         | 5           | 3         |
| **Business**     | $85–$450     | 100K–750K/mo    | $0.88            | 800+/hr         | Unlimited   | 15 days       | 7 days         | 3,000       | 1,000     |
| **Enterprise**   | $750+        | 1.5M+/mo        | $0.55            | Custom          | Unlimited   | 30 days       | 15 days        | Unlimited   | Unlimited |

> [!NOTE]
> Prices scale within each plan tier based on selected monthly volume (e.g., Basic covers 10K at $15/mo, 50K at $20/mo, 100K at $30/mo `(V)`). Hourly throttles for paid plans scale automatically with account sending reputation and history — the values above are starting baselines, not hard ceilings.

**Max email size:** 10 MB (Free and Basic plans); up to 30 MB (Business and Enterprise).

---

## 2. Technical Specs for Agents

> [!TIP]
> API rate limits govern request frequency per API token. Sending throughput is managed separately via per-plan throttling and reputation-based queuing. A 429 means you've exceeded the request rate; a throttle delay means you've exceeded the sending rate.

### API Rate Limits `(S)`

- **General limit:** 150 requests per 10 seconds per API token.
- **Stats API:** 10 requests per 60 seconds per account.
- **Email Logs (list):** 60 requests per 60 seconds per account.
- **Contacts API:** 200 requests per 60 seconds per account.
- **Batch endpoint:** Up to 500 individual messages per API call; each message supports up to 1,000 recipients per field (to/cc/bcc).

### SMTP Connection Limits `(S)`

- **SMTP hostname:** `live.smtp.mailtrap.io`
- **Port:** 587 (STARTTLS); also supports 25 and 465.
- **Username:** `api` (literal string).
- **Password:** Your API token (generate at https://mailtrap.io/api-tokens).
- **Concurrent connections:** Max 10 per account or sending IP.
- **Messages per SMTP connection:** Max 100.
- **Credentials are domain-specific:** Each verified domain has its own SMTP credentials accessible via the Integrations tab.

### Sending Streams `(S)`

- **Transactional endpoint:** `https://send.api.mailtrap.io/api/send` — for triggered, single-recipient transactional emails.
- **Bulk endpoint:** `https://bulk.api.mailtrap.io/api/send` — for marketing and promotional sends. Uses separate infrastructure to isolate transactional reputation.
- Both streams share identical request/response structure.

### Key Error Codes `(S)`

| Code  | Meaning                                              | Action                                              |
| :---- | :--------------------------------------------------- | :-------------------------------------------------- |
| `429` | Rate limit exceeded (API request frequency).         | Back off and retry with exponential delay.          |
| `422` | Invalid request payload (missing field, bad format). | Inspect error body; fix request before retrying.   |
| `401` | Invalid or missing API token.                        | Check `Authorization: Bearer <token>` header.       |
| `5xx` | Server-side error.                                   | Retry with exponential backoff; check status page.  |

---

## 3. Operational Health & Security

### Reliability Resources

- **Status Page:** https://status.mailtrap.info/
- **Status API:** `https://status.mailtrap.info/api` — JSON endpoint; poll for degraded/outage events before bulk sends.
- **Infrastructure:** Hosted on AWS; multi-region redundancy for the transactional sending pipeline.

### Trust & Compliance `(S)`

- **Certifications:** SOC 2 Type 2, ISO 27001.
- **GDPR:** GDPR-ready; Data Processing Agreement (DPA) available on request.
- **Trust Center:** https://trust.mailtrap.io/ — authoritative source for compliance documentation, sub-processor list, and security posture.

---

## 4. Integration Examples

### Transactional Send via Email API (cURL)

Send a single transactional email using the `/api/send` endpoint. Replace `<YOUR_API_TOKEN>` with a token from https://mailtrap.io/api-tokens.

```bash
curl -X POST "https://send.api.mailtrap.io/api/send" \
     -H "Authorization: Bearer <YOUR_API_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "from": {"email": "hello@yourdomain.com", "name": "Your App"},
       "to": [{"email": "recipient@example.com"}],
       "subject": "Welcome to Your App",
       "text": "Plain text body.",
       "html": "<p>HTML body.</p>",
       "category": "Onboarding",
       "custom_variables": {
         "user_id": "12345",
         "batch_id": "onboarding-2026-04"
       }
     }'
```

Expected response on success: `HTTP 200` with `{"success": true, "message_ids": ["<uuid>"]}`.

### SMTP Integration (Node.js / Nodemailer)

```javascript
const nodemailer = require("nodemailer");

const transport = nodemailer.createTransport({
  host: "live.smtp.mailtrap.io",
  port: 587,
  auth: {
    user: "api",
    pass: process.env.MAILTRAP_API_TOKEN,
  },
});

await transport.sendMail({
  from: '"Your App" <hello@yourdomain.com>',
  to: "recipient@example.com",
  subject: "Hello from Mailtrap SMTP",
  text: "Plain text body.",
});
```

---

## FSE Recipes (for Agents)

### Recipe 1 — Evaluate plan for a target monthly send volume

- **Input:** Target monthly email volume (e.g., 75,000 emails/month), whether a dedicated IP is required, whether multi-domain sending is needed, and maximum acceptable per-email cost.
- **Steps:**
  1. Look up the target volume in the Decision Matrix — identify candidate plans where the volume column covers the target.
  2. Cross-reference Section 1 (Pricing Tiers & Technical Limits) for per-plan price, overage rate, domain limits, and retention.
  3. If a dedicated IP is required, Business or higher is the minimum tier.
  4. Calculate total monthly cost: `plan_base_price + max(0, (volume - included_volume) / 1000 * overage_rate)`.
  5. State the recommended plan, the assumed volume, the cost calculation, and the row referenced.
- **Output:** A plan recommendation with: plan name, assumed monthly volume, estimated monthly cost (with formula), and 1–2 sentences of justification referencing specific table rows.
- **Success Event:** The agent names a specific plan, cites the Decision Matrix row, and provides a numeric cost estimate with explicit assumptions about volume and overage.

---

### Recipe 2 — Minimal transactional send with safe retries

- **Input:** A valid API token, a verified from-address domain, and a recipient email.
- **Steps:**
  1. Construct the request body per the Integration Examples section (required fields: `from`, `to`, `subject`, and at least one of `text`/`html`).
  2. POST to `https://send.api.mailtrap.io/api/send` with `Authorization: Bearer <token>`.
  3. On `200`: log the returned `message_ids` and exit.
  4. On `429`: wait `2^attempt` seconds (start at 2s, cap at 64s) and retry up to 5 times.
  5. On `5xx`: same backoff as 429.
  6. On `422` or `401`: do not retry — fix the request or credentials and re-run.
- **Output:** A working code snippet (language of choice) that sends one email and handles `429`/`5xx` with exponential backoff.
- **Success Event:** The snippet runs to completion, returns a `200` response, and logs a `message_id`. No uncaught exceptions on retry-able errors.

---

### Recipe 3 — Validate sending throttle limits before a large batch

- **Input:** Planned send volume for the session (e.g., 5,000 emails), current plan tier, and target send duration (e.g., 1 hour).
- **Steps:**
  1. Look up the hourly throttle for the current plan in Section 1 (e.g., Business: 800+/hr).
  2. Calculate required send rate: `total_volume / duration_hours` emails/hour.
  3. If required rate > hourly throttle: either extend the duration, upgrade the plan, or split into multiple SMTP connections (max 10 concurrent per Section 2).
  4. To validate live: send 10 emails in rapid succession via the API; observe whether any `429` responses are returned. If yes, the throttle is lower than expected and you should back off.
  5. If throttle is lower than the table suggests, note that paid plan throttles scale with reputation — a new account may start lower and increase over time.
- **Output:** A pre-flight check confirming whether the planned send rate is within documented limits, or a revised send schedule that respects them.
- **Success Event:** The agent produces a numeric comparison of `required_rate` vs `plan_throttle`, and either confirms compatibility or outputs a specific revised schedule with no `429` errors in the validation run.
