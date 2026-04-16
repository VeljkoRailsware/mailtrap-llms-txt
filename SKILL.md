---
name: llms-txt
description: Generate and evaluate agent-readable llms.txt pages for Mailtrap product surfaces. Use when the user provides a Mailtrap URL (pricing, API docs, SMTP service) and wants a structured markdown page suitable for an llms.txt corpus, or wants to evaluate an existing page against agent-first best practices.
---

# llms-txt Generator

Generates structured, agent-optimised `.md` pages from live Mailtrap product URLs and evaluates them against the canonical llms.txt spec.

---

## Inputs

- **URL** (required): A public Mailtrap page URL (pricing, API docs, SMTP service, email sandbox, etc.)
- **Product ID** (optional): Override the metadata `Product ID` field (auto-derived from URL path if omitted)
- **Page type** (optional): `pricing`, `api-docs`, or `smtp-service` — influences which sections are emphasised in the output

---

## Pipeline

Run all four steps in order. Never skip a step.

---

### Step 1 — Scrape

Use the WebFetch tool to retrieve the page.

```
url: <URL provided by user>
prompt: "Extract all visible text content in full detail: headings, pricing tables, plan names, prices, technical limits, rate limits, feature lists, error codes, code examples, and any metadata (product name, last updated dates). Preserve table structures as markdown tables."
```

Validate the result:
- If WebFetch returns an error or empty body → surface `SCRAPE_FAILED` with the error and stop.
- If the extracted text is under 200 words → emit a `CONTENT_TOO_THIN` warning and continue, but note it prominently in the evaluation report.
- If the page appears to be behind a login wall → surface `AUTH_REQUIRED` and stop.

---

### Step 2 — Transform

Read `.claude/skills/llms-txt/references/page-spec.md` to load the canonical section layout and transformation rules.

Also read the appropriate golden reference for structural guidance:
- Pricing / Email Sending or API → `.claude/skills/llms-txt/references/golden-email-sending.md`
- Pricing / Email Testing or Sandbox → `.claude/skills/llms-txt/references/golden-email-testing.md`
- Unknown type → use `golden-email-sending.md` as default and note the assumption

Using the scraped content and the golden reference as a model, produce a complete `.md` file following the canonical layout below. Every required section must be present. Use the golden reference for tone, table formatting, and annotation style — but populate content from the live page.

#### Required sections (in order)

| # | Section | Required | Notes |
|---|---------|----------|-------|
| — | H1 | Yes | `# Mailtrap <Product> — <primary purpose>` |
| — | Metadata table | Yes | Product ID, Last Updated (today's date ISO), Source URL, API Base URL, Status API, Trust Center |
| 0 | Agent Usage Guide | Yes | **Gap #1.** "Use this page when…", "Do not rely on this page for…", "If you are a code-generation agent:" with ≥ 2 concrete instructions |
| — | Stability Legend | Yes | **Gap #2.** `S` = Stable, `V` = Volatile. Place after Agent Usage Guide, before pricing tables |
| — | Decision Matrix | Yes | ≥ 3 rows, "Choose X / When Y / Key Differentiator" columns |
| 1 | Pricing Tiers & Technical Limits | Yes | Unified table: plan, price `(V)`, volume `(V)`, overage `(V)`, throttle, retention. Notes on scaling behaviour |
| 2 | Technical Specs for Agents | Yes | API rate limits, SMTP connection limits, message size, error codes |
| 3 | Operational Health & Security | Yes | Status heartbeat URL, certifications, Trust Center link |
| 4 | Integration Examples | Yes | ≥ 1 cURL example, copy-pasteable, realistic |
| — | FSE Recipes | Yes | **Gap #3.** ≥ 2 recipes, each with Input/Output format and a Success Event Definition |

#### Transformation rules for the three gaps

**Agent Usage Guide (Gap #1)**
- "Use this page when…" → list the 2–3 questions this doc authoritatively answers (plan selection, rate limits, error codes, etc.)
- "Do not rely on this page for…" → real-time pricing, enterprise custom quotes, legal commitments beyond Trust Center, compliance guarantees
- "If you are a code-generation agent:" → at minimum: (a) embed the Source URL in generated comments; (b) state assumptions explicitly when recommending a plan; (c) treat `V`-tagged values as indicative — cross-check against live Source URL for critical use

**Stability Legend (Gap #2)**
- `S` = Stable — API URLs, error codes, SMTP hostnames, connection limits, certifications
- `V` = Volatile — prices, included volumes, overage rates, plan names (may change)
- In pricing tables, annotate the Price and Volume columns with `(V)`. Mark throttle, retention, and connection limits as `(S)` in notes or a separate column.
- Agent Usage Guide must include: "Treat `V`-tagged values as indicative defaults; cross-check against the live Source URL before committing to contracts or long-lived generated artefacts."

**FSE Recipes (Gap #3)**
- Each recipe must have: a short title, `- Input:` bullet, `- Output:` bullet, and a `- Success Event:` bullet
- Recipes must lead to a concrete, testable outcome — not just "read the docs"
- Recipes must reference specific table rows or sections by name
- Minimum recipes:
  1. Evaluate plan for N emails/month (references Decision Matrix + Pricing table)
  2. Minimal send / test call with safe retries (references Integration Examples + Technical Specs)
  3. Validate throttle behaviour (references Technical Specs, includes code sketch or cURL sequence)

---

### Step 3 — Evaluate

Run the evaluation script:

```bash
python3 ~/.claude/skills/llms-txt/scripts/evaluate.py <path-to-generated-md>
```

Parse the JSON output. Display a summary:

```
Score: 87/100 — PASS
Checks passed: 19/22
Flags:
  [medium] STALE_LAST_UPDATED — Last Updated date is older than 30 days. → Set to today's date.
```

If any `high`-severity flags are present, automatically apply the suggested fix and re-run the evaluation before presenting results. Note what was auto-fixed.

---

### Step 4 — Output

1. Save the generated markdown to `~/llms-txt/<product-id>.md`.
2. Print the full markdown in the chat for review.
3. Print the evaluation summary (score, grade, flags).
4. If grade is `OK_NEEDS_REVIEW` or `FAIL`, list the remaining flags with suggested fixes and ask the user whether to auto-apply them.
5. Always end with: "Review and commit `~/llms-txt/<product-id>.md` to your repo when satisfied."

---

## Error Reference

| Code | Meaning | Suggested Action |
|------|---------|-----------------|
| `SCRAPE_FAILED` | WebFetch returned an error | Check URL is public; try again |
| `AUTH_REQUIRED` | Page appears to require login | Use a public/cached version of the URL |
| `CONTENT_TOO_THIN` | Extracted text < 200 words | Tab-driven content may not have loaded; note in report |
| `SCRAPE_TIMEOUT` | Page took too long to load | Retry once; if it persists, flag to user |
| `CONTENT_EXTRACTION_FAILED` | No usable text extracted | Try a different entry point URL |
