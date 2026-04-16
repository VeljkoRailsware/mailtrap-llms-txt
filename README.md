# mailtrap-llms-txt

A Claude Code skill that generates structured, agent-optimised `.md` pages from live Mailtrap product URLs — and evaluates them against a canonical spec.

Designed to produce [llms.txt](https://llmstxt.org/)-style reference pages that LLM agents can consume reliably: authoritative pricing data, rate limits, SMTP parameters, error codes, and task recipes, all in a consistent, annotated format.

---

## What it does

Run `/llms-txt <URL>` in Claude Code and the skill will:

1. **Scrape** the live Mailtrap page via WebFetch
2. **Transform** the content into a canonical `.md` file (all required sections, correct order, `S`/`V` stability annotations)
3. **Evaluate** the output against 22 rule-based checks (0–100 score, PASS/OK_NEEDS_REVIEW/FAIL)
4. **Save** the result to `~/llms-txt/<product-id>.md` and print the evaluation summary

Auto-fixes any high-severity issues before reporting results.

---

## Installation

Copy the skill into your Claude Code skills directory:

```bash
cp -r . ~/.claude/skills/llms-txt
```

That's it. No external dependencies — the evaluation script (`scripts/evaluate.py`) uses Python 3 stdlib only.

---

## Usage

```
/llms-txt <URL>
```

**Examples:**

```
/llms-txt https://mailtrap.io/email-api/
/llms-txt https://mailtrap.io/smtp-service/
/llms-txt https://mailtrap.io/pricing/?tab=email-sending
/llms-txt https://mailtrap.io/pricing/?tab=email-sandbox
```

Generated files are saved to `~/llms-txt/<product-id>.md`.

---

## Output format

Every generated page follows this section order:

| Section | Purpose |
| :------ | :------ |
| H1 + Metadata table | Product identity, Source URL, API endpoints |
| Agent Usage Guide | When to use / not use this page; code-gen agent instructions |
| Stability Legend | `S` = stable (safe to cache), `V` = volatile (cross-check before use) |
| Decision Matrix | ≥ 3 rows: Choose / When / Key Differentiator |
| 1. Pricing Tiers & Technical Limits | Unified plan table with price `(V)`, volume `(V)`, throttle, retention |
| 2. Technical Specs for Agents | API rate limits, SMTP connection limits, error codes |
| 3. Operational Health & Security | Status page, certifications, Trust Center |
| 4. Integration Examples | Copy-pasteable cURL / SDK snippets |
| FSE Recipes | ≥ 3 structured task recipes: Input → Steps → Output → Success Event |

The `S`/`V` annotation system lets agents know which values are safe to cache (SMTP hostnames, error codes, connection limits) vs. which need live verification (prices, included volumes, overage rates).

---

## Evaluation

The skill runs `scripts/evaluate.py` against every generated file. The script checks 22 rules across structure, content, and format:

```
Score: 100/100 — PASS
Checks passed: 22/22
Flags: none
```

**Scoring:**
- High-severity failures: −5 pts each
- Medium-severity failures: −3 pts each
- Low-severity failures: −1 pt each
- PASS: score ≥ 85 with no high-severity flags
- OK_NEEDS_REVIEW: score ≥ 60
- FAIL: score < 60

Run it standalone against any `.md` file:

```bash
python3 scripts/evaluate.py path/to/file.md
```

---

## Repo structure

```
mailtrap-llms-txt/
├── SKILL.md                          # Claude Code skill definition
├── references/
│   ├── page-spec.md                  # Canonical section layout and transformation rules
│   ├── golden-email-sending.md       # Reference file: Email API / SMTP sending
│   └── golden-email-testing.md       # Reference file: Email Testing (Sandbox)
└── scripts/
    └── evaluate.py                   # Rule-based evaluator (22 checks, JSON output)
```

---

## Requirements

- [Claude Code](https://claude.ai/code) with skills support
- Python 3.8+ (stdlib only — no pip installs required)
- A public Mailtrap product URL

---

## License

MIT
