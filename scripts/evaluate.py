#!/usr/bin/env python3
"""
evaluate.py — Rule-based evaluation script for Mailtrap llms.txt pages.

Usage:
    python3 evaluate.py <path-to-markdown-file>

Output:
    JSON to stdout with score, grade, flags, and check summary.
"""

import sys
import re
import json
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Check definitions
# ---------------------------------------------------------------------------

class Check:
    def __init__(self, check_id, severity, message, suggested_fix):
        self.check_id = check_id
        self.severity = severity      # "high" | "medium" | "low"
        self.message = message
        self.suggested_fix = suggested_fix

    def to_dict(self):
        return {
            "check_id": self.check_id,
            "severity": self.severity,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
        }


def run_checks(content: str) -> list[Check]:
    """Run all checks against markdown content. Return list of failed checks."""
    lines = content.splitlines()
    flags = []

    def fail(check_id, severity, message, suggested_fix):
        flags.append(Check(check_id, severity, message, suggested_fix))

    # --- H1 ---
    h1_lines = [l for l in lines if re.match(r'^# [^#]', l)]
    if not h1_lines:
        fail(
            "MISSING_H1",
            "high",
            "No H1 heading found.",
            "Add a top-level heading: '# Mailtrap <Product> — <primary purpose>'."
        )

    # --- Metadata table ---
    has_product_id = bool(re.search(r'\*\*Product ID\*\*', content, re.IGNORECASE))
    has_last_updated = bool(re.search(r'\*\*Last Updated\*\*', content, re.IGNORECASE))
    has_source_url = bool(re.search(r'\*\*Source URL\*\*', content, re.IGNORECASE))

    if not (has_product_id and has_last_updated and has_source_url):
        missing = []
        if not has_product_id: missing.append("Product ID")
        if not has_last_updated: missing.append("Last Updated")
        if not has_source_url: missing.append("Source URL")
        fail(
            "MISSING_METADATA_TABLE",
            "high",
            f"Metadata table is missing required fields: {', '.join(missing)}.",
            "Add a metadata table with at minimum: Product ID, Last Updated, Source URL."
        )

    # --- Stale Last Updated ---
    date_match = re.search(r'\*\*Last Updated\*\*\s*\|?\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        try:
            last_updated = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
            delta = (date.today() - last_updated).days
            if delta > 30:
                fail(
                    "STALE_LAST_UPDATED",
                    "medium",
                    f"Last Updated date ({last_updated}) is {delta} days ago (> 30 day threshold).",
                    f"Update Last Updated to today's date: {date.today().isoformat()}."
                )
        except ValueError:
            pass

    # --- Agent Usage Guide ---
    if not re.search(r'##\s+Agent Usage Guide', content, re.IGNORECASE):
        fail(
            "MISSING_AGENT_USAGE_GUIDE",
            "high",
            "'## Agent Usage Guide' section is missing.",
            "Add a '## Agent Usage Guide' section with use-when, do-not, and code-gen-agent subsections."
        )
    else:
        if not re.search(r'Use this page when', content, re.IGNORECASE):
            fail(
                "AGENT_GUIDE_MISSING_USE_WHEN",
                "high",
                "Agent Usage Guide does not contain 'Use this page when' guidance.",
                "Add a 'Use this page when…' bullet listing the primary use cases."
            )
        if not re.search(r'Do not rely on', content, re.IGNORECASE):
            fail(
                "AGENT_GUIDE_MISSING_DO_NOT",
                "high",
                "Agent Usage Guide does not contain 'Do not rely on this page' guidance.",
                "Add a 'Do not rely on this page for…' bullet listing out-of-scope uses."
            )
        if not re.search(r'code.generation agent', content, re.IGNORECASE):
            fail(
                "AGENT_GUIDE_MISSING_CODE_GEN",
                "medium",
                "Agent Usage Guide does not have a 'code-generation agent' instruction block.",
                "Add an 'If you are a code-generation agent:' section with ≥ 2 concrete instructions."
            )

    # --- Stability Legend ---
    if not re.search(r'Stability Legend', content, re.IGNORECASE):
        fail(
            "MISSING_STABILITY_LEGEND",
            "high",
            "'Stability Legend' section is missing.",
            "Add a '### Stability Legend' subsection defining S (Stable) and V (Volatile) tags."
        )
    else:
        if not re.search(r'`S`.*[Ss]table', content):
            fail(
                "LEGEND_MISSING_S_TAG",
                "medium",
                "Stability Legend does not define the `S` (Stable) tag.",
                "Add: '`S` — Stable. Changes rarely; safe to cache in agent memory.'"
            )
        if not re.search(r'`V`.*[Vv]olatile', content):
            fail(
                "LEGEND_MISSING_V_TAG",
                "medium",
                "Stability Legend does not define the `V` (Volatile) tag.",
                "Add: '`V` — Volatile. Pricing/quota values; check live Source URL for critical use.'"
            )

    # --- Decision Matrix ---
    if not re.search(r'##\s+Decision Matrix', content, re.IGNORECASE):
        fail(
            "MISSING_DECISION_MATRIX",
            "medium",
            "'## Decision Matrix' section is missing.",
            "Add a '## Decision Matrix' section with ≥ 3 rows: Choose / When / Key Differentiator."
        )
    else:
        # Count data rows in the Decision Matrix section
        dm_match = re.search(
            r'##\s+Decision Matrix.*?(?=\n##\s|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if dm_match:
            dm_section = dm_match.group(0)
            # Count table rows (lines starting with | that aren't header or separator)
            table_rows = [
                l for l in dm_section.splitlines()
                if re.match(r'^\s*\|', l) and not re.match(r'^\s*\|[\s:|-]+\|', l)
            ]
            # Subtract 1 for the header row
            data_rows = max(0, len(table_rows) - 1)
            if data_rows < 3:
                fail(
                    "DECISION_MATRIX_TOO_SMALL",
                    "medium",
                    f"Decision Matrix has only {data_rows} data row(s); minimum is 3.",
                    "Add more plan rows to the Decision Matrix table (≥ 3 data rows)."
                )

    # --- Pricing table ---
    # Look for a table with ≥ 3 columns in a pricing-related section
    pricing_tables = []
    for line in lines:
        if re.match(r'^\s*\|', line):
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if len(cols) >= 3:
                pricing_tables.append(line)

    if not pricing_tables:
        fail(
            "MISSING_PRICING_TABLE",
            "medium",
            "No table with ≥ 3 columns found.",
            "Add a pricing/limits table with at least Plan, Price, and one limit column."
        )

    # --- Technical Specs ---
    if not re.search(r'##\s+2\.\s+Technical Specs', content, re.IGNORECASE):
        fail(
            "MISSING_TECH_SPECS",
            "medium",
            "'## 2. Technical Specs for Agents' section is missing.",
            "Add a '## 2. Technical Specs for Agents' section with API rate limits and connection limits."
        )

    # --- Operational Health ---
    if not re.search(r'##\s+3\.\s+Operational Health', content, re.IGNORECASE):
        fail(
            "MISSING_OPS_HEALTH",
            "low",
            "'## 3. Operational Health & Security' section is missing.",
            "Add a '## 3. Operational Health & Security' section with status page and Trust Center links."
        )

    # --- Integration Examples ---
    if not re.search(r'##\s+4\.\s+Integration Examples', content, re.IGNORECASE):
        fail(
            "MISSING_INTEGRATION_EXAMPLES",
            "low",
            "'## 4. Integration Examples' section is missing.",
            "Add a '## 4. Integration Examples' section with ≥ 1 copy-pasteable cURL example."
        )

    # --- Code block ---
    if not re.search(r'```', content):
        fail(
            "MISSING_CODE_BLOCK",
            "medium",
            "No fenced code block found.",
            "Add at least one fenced code block (e.g., a cURL example in Integration Examples)."
        )

    # --- FSE Recipes ---
    if not re.search(r'##\s+FSE Recipes', content, re.IGNORECASE):
        fail(
            "MISSING_FSE_RECIPES",
            "high",
            "'## FSE Recipes (for Agents)' section is missing.",
            "Add a '## FSE Recipes (for Agents)' section with ≥ 2 recipes (Input/Output/Success Event format)."
        )
    else:
        fse_match = re.search(
            r'##\s+FSE Recipes.*?(?=\n##\s|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if fse_match:
            fse_section = fse_match.group(0)
            if not re.search(r'\*\*Input', fse_section, re.IGNORECASE):
                fail(
                    "FSE_MISSING_INPUT_OUTPUT",
                    "medium",
                    "FSE Recipes section does not contain 'Input:' / 'Output:' structured format.",
                    "Format each recipe with '- **Input:**' and '- **Output:**' bullets."
                )
            if not re.search(r'Success Event', fse_section, re.IGNORECASE):
                fail(
                    "FSE_MISSING_SUCCESS_DEF",
                    "medium",
                    "FSE Recipes section does not contain a 'Success Event' definition.",
                    "Add '- **Success Event:**' to each recipe with an observable success condition."
                )

    # --- Content length ---
    words = len(re.findall(r'\b\w+\b', content))
    if words < 400:
        fail(
            "CONTENT_TOO_SHORT",
            "high",
            f"Content is only {words} words (minimum: 400).",
            "Expand the content — add more detail to pricing table notes, technical specs, or FSE recipes."
        )

    # --- Table count ---
    table_count = len([l for l in lines if re.match(r'^\s*\|', l) and '---' not in l and l.count('|') >= 3])
    # Rough count: distinct table blocks
    in_table = False
    table_blocks = 0
    for line in lines:
        is_table_line = bool(re.match(r'^\s*\|', line))
        if is_table_line and not in_table:
            table_blocks += 1
            in_table = True
        elif not is_table_line:
            in_table = False

    if table_blocks < 2:
        fail(
            "LOW_TABLE_COUNT",
            "low",
            f"Only {table_blocks} markdown table block(s) found; minimum recommended is 2.",
            "Add additional tables for the Decision Matrix and Pricing Tiers if missing."
        )

    return flags


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

TOTAL_CHECKS = 22

SEVERITY_WEIGHTS = {
    "high": 5,
    "medium": 3,
    "low": 1,
}

MAX_DEDUCTION = sum([
    # high flags (10 checks × 5)
    10 * SEVERITY_WEIGHTS["high"],
    # medium flags (7 checks × 3)
    7 * SEVERITY_WEIGHTS["medium"],
    # low flags (5 checks × 1)
    5 * SEVERITY_WEIGHTS["low"],
])


def compute_score(flags: list[Check]) -> int:
    deduction = sum(SEVERITY_WEIGHTS.get(f.severity, 0) for f in flags)
    # Scale to 0-100
    raw = max(0, 100 - round((deduction / MAX_DEDUCTION) * 100))
    return raw


def compute_grade(score: int, flags: list[Check]) -> str:
    has_high = any(f.severity == "high" for f in flags)
    if score >= 85 and not has_high:
        return "PASS"
    elif score >= 60:
        return "OK_NEEDS_REVIEW"
    else:
        return "FAIL"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: evaluate.py <path-to-markdown>"}))
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(json.dumps({"ok": False, "error": f"File not found: {path}"}))
        sys.exit(1)
    except OSError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(1)

    flags = run_checks(content)
    score = compute_score(flags)
    grade = compute_grade(score, flags)
    checks_failed = len(flags)
    checks_passed = TOTAL_CHECKS - checks_failed

    result = {
        "ok": True,
        "score": score,
        "grade": grade,
        "checks_passed": checks_passed,
        "checks_total": TOTAL_CHECKS,
        "flags": [f.to_dict() for f in flags],
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
