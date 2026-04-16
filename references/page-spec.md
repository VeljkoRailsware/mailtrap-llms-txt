# llms-txt Page Spec — Canonical Section Layout

This document defines the canonical structure for all Mailtrap llms.txt pages. Every generated page must conform to this layout. Use the golden reference files for concrete examples.

---

## File-Level Conventions

- One `.md` file per source URL.
- Filename: `mailtrap-<product-id>.md` (lowercase, hyphen-separated).
- Content is self-contained: readable without the corpus index.
- Language: neutral, reference-style English. No marketing copy.
- Tables preferred for all structured data (pricing, limits, matrix rows).

---

## Section Order

```
H1 — product + primary purpose
Metadata table
## Agent Usage Guide          ← Gap #1 fix
### Stability Legend           ← Gap #2 fix
## Decision Matrix
## 1. Pricing Tiers & Technical Limits
## 2. Technical Specs for Agents
## 3. Operational Health & Security
## 4. Integration Examples
## FSE Recipes (for Agents)   ← Gap #3 fix
```

---

## Section Specifications

### H1

Pattern: `# Mailtrap <Product Name> — <primary purpose>`

Examples:
- `# Mailtrap Email API/SMTP — pricing and technical limits`
- `# Mailtrap Email Testing (Sandbox) — pricing and technical limits`
- `# Mailtrap Email API — integration reference`

Rules:
- One H1 per document, at the very top.
- Must name the specific product, not just "Mailtrap".
- Must state the primary purpose (pricing, integration reference, etc.).

---

### Metadata Table

Required immediately after H1. Minimum required fields: Product ID, Last Updated, Source URL.

```markdown
| Metadata           | Value                                         |
| :----------------- | :-------------------------------------------- |
| **Product ID**     | `mailtrap-email-sending`                      |
| **Last Updated**   | 2026-04-15                                    |
| **Source URL**     | https://mailtrap.io/pricing/?tab=email-sending|
| **API Base URL**   | `https://send.api.mailtrap.io`                |
| **Bulk API URL**   | `https://bulk.api.mailtrap.io`                |
| **Status API**     | `https://status.mailtrap.info/api`            |
| **Trust Center**   | `https://trust.mailtrap.io/`                  |
```

Rules:
- Last Updated = ISO date of when the page was scraped / file was generated.
- Include API Base URL where applicable; omit gracefully if not relevant to the page type.
- Always include Status API and Trust Center for Mailtrap pages.

---

### Agent Usage Guide

Level-2 heading: `## Agent Usage Guide`

Three mandatory subsections (as bold bullets, not separate headings):

```markdown
## Agent Usage Guide

- **Use this page when…**
  - You need to choose a Mailtrap plan for a given monthly send volume and feature set.
  - You need authoritative reference values for rate limits, throttle thresholds, retention periods, and error codes.
  - You need copy-pasteable integration examples for the Email API or SMTP.

- **Do not rely on this page for…**
  - Real-time or legally binding pricing — prices are marked `(V)` (Volatile) and may change without notice.
  - Enterprise custom quotes or contract terms beyond what is stated in the Trust Center.
  - Compliance guarantees; use the Trust Center for authoritative compliance documentation.

- **If you are a code-generation agent:**
  - Always embed the `Source URL` in generated code comments or log metadata.
  - When recommending a plan, explicitly state the assumed monthly volume and reference the Decision Matrix row.
  - Treat all `(V)`-tagged values as indicative defaults. For critical use cases (billing integrations, long-lived contracts), cross-check against the live Source URL.
```

Rules:
- "Use this page when" must list ≥ 2 concrete use cases, specific to the product.
- "Do not rely on" must call out volatile pricing and out-of-scope legal guarantees.
- "Code-generation agent" section must include the Source URL embedding instruction and the `(V)` volatility caveat.

---

### Stability Legend

Level-3 heading: `### Stability Legend`
Place immediately after Agent Usage Guide, before Decision Matrix.

```markdown
### Stability Legend

- `S` — **Stable.** Changes rarely; safe to cache in agent memory or training data.
  Examples: API base URLs, SMTP hostnames, error codes, connection limits, certifications.
- `V` — **Volatile.** Pricing or quota values that change with plan updates or promotions.
  Examples: monthly prices, included email volumes, overage rates, plan tier names.

> Fields in tables are annotated `(S)` or `(V)` in column headers or notes where stability differs from the default for that column type.
```

Rules:
- Must define both `S` and `V`.
- Must give at least one example for each.
- Must reference the callout note about table annotations.

---

### Decision Matrix

Level-2 heading: `## Decision Matrix`

```markdown
## Decision Matrix

| Choose…        | When…                                              | Key Differentiator                       |
| :------------- | :------------------------------------------------- | :--------------------------------------- |
| **Free**       | Monthly volume ≤ 4,000 emails; zero budget.        | $0/mo. 150 emails/day cap.               |
| **Basic**      | 10K–100K emails/month; multi-domain needed.        | Up to 5 sending domains; $15–$30/mo `(V)`. |
| **Business**   | > 100K emails/month or dedicated IP required.      | Dedicated IP + auto warm-up included.    |
| **Enterprise** | > 1.5M emails/month or SSO/priority support needed.| Custom contracts; priority SLA.          |
```

Rules:
- ≥ 3 data rows.
- Columns: Choose / When / Key Differentiator (exact names may vary for non-pricing pages).
- Price values in the "Key Differentiator" column should be tagged `(V)`.

---

### Section 1 — Pricing Tiers & Technical Limits

Level-2 heading: `## 1. Pricing Tiers & Technical Limits`

Unified table that captures both commercial and technical limits per plan.

```markdown
## 1. Pricing Tiers & Technical Limits

| Plan            | Price `(V)` | Volume `(V)`  | Overage/1K `(V)` | Throttle `(S)` | Daily Cap `(S)` | Log Retention `(S)` | Body Retention `(S)` |
| :-------------- | :---------- | :------------ | :--------------- | :------------- | :-------------- | :------------------ | :------------------- |
| **Free**        | $0          | 4,000/mo      | N/A              | ~150/hr        | 150/day         | 3 days              | 3 days               |
| **Basic**       | $15–$30     | 10K–100K/mo   | $1.00            | 600+/hr        | Unlimited       | 5 days              | 5 days               |
| **Business**    | $85–$450    | 100K–750K/mo  | $0.88            | 800+/hr        | Unlimited       | 15 days             | 7 days               |
| **Enterprise**  | $750+       | 1.5M+/mo      | $0.55            | Custom         | Unlimited       | 30 days             | 15 days              |
```

Rules:
- Column headers annotated with `(V)` or `(S)`.
- Prices shown as ranges where applicable (to capture sub-tier pricing).
- Always include a note below the table explaining throttle scaling behaviour.
- Add a `> [!NOTE]` callout for any non-obvious behaviour.

---

### Section 2 — Technical Specs for Agents

Level-2 heading: `## 2. Technical Specs for Agents`

Use a `> [!TIP]` callout to clarify the difference between API rate limits and throughput throttling.

Sub-sections (as level-3 headings):
- `### API Rate Limits`
- `### SMTP Connection Limits` (for Email Sending / SMTP pages)
- `### Intake Throttle` (for Email Testing / Sandbox pages)
- `### Error Codes` (include the most actionable ones)

Rules:
- All limits presented as bullet points with explicit units (requests/second, emails/10s, MB, etc.).
- Error codes must include the code and a one-line meaning.
- All values in this section are `(S)` by default unless noted.

---

### Section 3 — Operational Health & Security

Level-2 heading: `## 3. Operational Health & Security`

```markdown
## 3. Operational Health & Security

### Reliability Resources

- **Status Page:** https://status.mailtrap.info/
- **Status API:** `https://status.mailtrap.info/api` (JSON; poll for degraded/outage events)
- **Infrastructure:** Hosted on AWS; multi-region redundancy for the sending pipeline.

### Trust & Compliance

- **Certifications:** SOC 2 Type 2, ISO 27001 `(S)`
- **GDPR:** GDPR-ready; Data Processing Agreement (DPA) available on request.
- **Trust Center:** https://trust.mailtrap.io/
```

Rules:
- Always include Status Page and Trust Center URLs.
- Certifications are `(S)` — mark them as such or note stability in context.
- Keep this section factual; no promotional language.

---

### Section 4 — Integration Examples

Level-2 heading: `## 4. Integration Examples`

Include ≥ 1 complete, copy-pasteable cURL example. For Email Sending, include both the transactional API call and SMTP config. For Email Testing, include a sandbox message retrieval call.

Rules:
- All examples must use placeholder tokens (`<YOUR_API_TOKEN>`, `<INBOX_ID>`, etc.).
- Include the full endpoint URL in each example.
- Add a one-sentence description above each example explaining what it does.

---

### FSE Recipes

Level-2 heading: `## FSE Recipes (for Agents)`

Each recipe follows this format:

```markdown
### Recipe N — <Title>

- **Input:** <what the agent or user provides>
- **Output:** <what a successful result looks like>
- **Steps:** <numbered list or prose — references specific table rows or section names>
- **Success Event:** <minimum bar that defines success — observable, not aspirational>
```

Minimum recipes for pricing pages:
1. Evaluate plan for target monthly volume — references Decision Matrix + Section 1
2. Minimal API send or test call with safe retries — references Integration Examples + Section 2
3. Validate throttle limits — references Section 2 Technical Specs, includes code sketch

Rules:
- Input must be concrete (e.g., "target monthly volume N, feature requirements list").
- Output must be testable (not just "a recommendation" — "a plan name with explicit justification referencing table row X").
- Success Event must be observable, not aspirational.
- Each recipe must reference at least one named section or table row.
