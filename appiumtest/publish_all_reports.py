"""
publish_all_reports.py
Reads all 4 DairyDash test xlsx reports and writes a full
test-case-name listing + stats to $GITHUB_STEP_SUMMARY.
"""
import os
import sys
import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import openpyxl
except ImportError:
    os.system("pip install openpyxl")
    import openpyxl

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

REPORTS = {
    "appium":   os.path.join(SCRIPT_DIR, "appium report.xlsx"),
    "selenium": os.path.join(SCRIPT_DIR, "selineum report.xlsx"),
    "load":     os.path.join(SCRIPT_DIR, "Baseline_Load_Test_PASS_ONLY_20260622_140125.xlsx"),
    "security": os.path.join(SCRIPT_DIR, "Security_Control_Test_Cases_Report_400_v2.xlsx"),
}

# ── Helper: read a named sheet, skipping the merged-title first row ──────────
def read_sheet(filepath, sheet_name, header_row_index=1):
    """Return (headers, list_of_dicts). header_row_index is 0-based."""
    wb = openpyxl.load_workbook(filepath, data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) <= header_row_index:
        return [], []
    headers = [str(c).strip() if c is not None else "" for c in rows[header_row_index]]
    data = []
    for row in rows[header_row_index + 1:]:
        if any(c is not None for c in row):
            data.append(dict(zip(headers, row)))
    return headers, data

def status_emoji(val):
    v = str(val).strip().upper() if val else ""
    if any(x in v for x in ("PASS", "OK", "SUCCESS", "PASSED", "✅")):
        return "✅ PASS"
    if any(x in v for x in ("FAIL", "ERROR", "FAILED", "❌")):
        return "❌ FAIL"
    return f"🔵 {val}"

def escape(val, limit=80):
    s = str(val).replace("|", "\\|").replace("\n", " ").strip() if val is not None else ""
    return s[:limit] + ("…" if len(s) > limit else "")

def count_pass_fail(data, status_col):
    passed = failed = 0
    for r in data:
        v = str(r.get(status_col, "")).strip().upper()
        if any(x in v for x in ("PASS", "OK", "SUCCESS")):
            passed += 1
        elif any(x in v for x in ("FAIL", "ERROR")):
            failed += 1
    return passed, failed

# ─────────────────────────────────────────────────────────────────────────────
# SECTION BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def section_appium(md):
    label = "📱 Appium Mobile E2E Report (400 Cases)"
    path = REPORTS["appium"]
    md.append(f"## {label}\n")

    if not os.path.isfile(path):
        md.append(f"> ❌ File not found: `{os.path.basename(path)}`\n")
        return

    # --- Stats from Module Summary sheet ---
    _, mod_data = read_sheet(path, "Module Summary", header_row_index=1)
    if mod_data:
        md.append("### Module-wise Results\n")
        md.append("| Module | Total | Passed | Failed | Errors | Pass % |")
        md.append("|---|---|---|---|---|---|")
        for r in mod_data:
            md.append(f"| {escape(r.get('Module'))} | {r.get('Total')} | ✅ {r.get('Passed')} | ❌ {r.get('Failed')} | ⚠️ {r.get('Errors')} | **{r.get('Pass %')}** |")
        md.append("")

    # --- All test cases from Test Results sheet ---
    _, tc_data = read_sheet(path, "Test Results", header_row_index=1)
    passed, failed = count_pass_fail(tc_data, "Status")
    total = len(tc_data)
    rate = f"{(passed/total*100):.1f}%" if total else "N/A"

    md.append(f"### All Test Cases — {total} total | ✅ {passed} Passed | ❌ {failed} Failed | 📈 {rate}\n")
    md.append("| TC ID | Module | Test Title | Status | Duration | Remarks |")
    md.append("|---|---|---|---|---|---|")
    for r in tc_data:
        md.append(
            f"| `{escape(r.get('TC ID'))}` "
            f"| {escape(r.get('Module'))} "
            f"| {escape(r.get('Test Title'))} "
            f"| {status_emoji(r.get('Status'))} "
            f"| {escape(r.get('Duration'))} "
            f"| {escape(r.get('Remarks'))} |"
        )
    md.append("")


def section_selenium(md):
    label = "🌐 Selenium Web E2E Report (400 Cases)"
    path = REPORTS["selenium"]
    md.append(f"## {label}\n")

    if not os.path.isfile(path):
        md.append(f"> ❌ File not found: `{os.path.basename(path)}`\n")
        return

    # --- Stats ---
    _, mod_data = read_sheet(path, "Module Summary", header_row_index=1)
    if mod_data:
        md.append("### Module-wise Results\n")
        md.append("| Module | Total | Passed | Failed | Errors | Pass % |")
        md.append("|---|---|---|---|---|---|")
        for r in mod_data:
            md.append(f"| {escape(r.get('Module'))} | {r.get('Total')} | ✅ {r.get('Passed')} | ❌ {r.get('Failed')} | ⚠️ {r.get('Errors')} | **{r.get('Pass %')}** |")
        md.append("")

    # --- All test cases ---
    _, tc_data = read_sheet(path, "Test Results", header_row_index=1)
    passed, failed = count_pass_fail(tc_data, "Status")
    total = len(tc_data)
    rate = f"{(passed/total*100):.1f}%" if total else "N/A"

    md.append(f"### All Test Cases — {total} total | ✅ {passed} Passed | ❌ {failed} Failed | 📈 {rate}\n")
    md.append("| TC ID | Module | Test Title | Status | Duration | Remarks |")
    md.append("|---|---|---|---|---|---|")
    for r in tc_data:
        md.append(
            f"| `{escape(r.get('TC ID'))}` "
            f"| {escape(r.get('Module'))} "
            f"| {escape(r.get('Test Title'))} "
            f"| {status_emoji(r.get('Status'))} "
            f"| {escape(r.get('Duration'))} "
            f"| {escape(r.get('Remarks'))} |"
        )
    md.append("")


def section_load(md):
    label = "⚡ Baseline Load Test Report (PASS ONLY)"
    path = REPORTS["load"]
    md.append(f"## {label}\n")

    if not os.path.isfile(path):
        md.append(f"> ❌ File not found: `{os.path.basename(path)}`\n")
        return

    # --- All 400 test cases ---
    _, tc_data = read_sheet(path, "400 Test Cases", header_row_index=1)
    passed, failed = count_pass_fail(tc_data, "Result")
    total = len(tc_data)
    rate = f"{(passed/total*100):.1f}%" if total else "N/A"

    md.append(f"### All Test Cases — {total} total | ✅ {passed} Passed | ❌ {failed} Failed | 📈 {rate}\n")
    md.append("| TC # | Test Case Name | Category | Endpoint | Method | Expected | Actual | Resp Time (ms) | Result |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for r in tc_data:
        md.append(
            f"| `{escape(r.get('TC #'))}` "
            f"| {escape(r.get('Test Case Name'))} "
            f"| {escape(r.get('Category'))} "
            f"| `{escape(r.get('Endpoint'))}` "
            f"| **{escape(r.get('Method'))}** "
            f"| {escape(r.get('Expected'))} "
            f"| {escape(r.get('Actual'))} "
            f"| {escape(r.get('Response Time (ms)'))} "
            f"| {status_emoji(r.get('Result'))} |"
        )
    md.append("")


def section_security(md):
    label = "🛡️ Security Control Test Cases Report (400 v2)"
    path = REPORTS["security"]
    md.append(f"## {label}\n")

    if not os.path.isfile(path):
        md.append(f"> ❌ File not found: `{os.path.basename(path)}`\n")
        return

    _, tc_data = read_sheet(path, "Security Test Results", header_row_index=1)
    passed, failed = count_pass_fail(tc_data, "Verdict")
    total = len(tc_data)
    rate = f"{(passed/total*100):.1f}%" if total else "N/A"

    # Severity counts
    severity_counts = {}
    for r in tc_data:
        sev = str(r.get("Severity", "Unknown")).strip()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    md.append("### Severity Breakdown\n")
    md.append("| Severity | Count |")
    md.append("|---|---|")
    for sev, count in sorted(severity_counts.items()):
        emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢", "Info": "🔵"}.get(sev, "⚪")
        md.append(f"| {emoji} {sev} | **{count}** |")
    md.append("")

    md.append(f"### All Test Cases — {total} total | ✅ {passed} Passed | ❌ {failed} Failed | 📈 {rate}\n")
    md.append("| Test ID | Component / Route | Control Area | Description / Vulnerability Audited | Severity | Verdict |")
    md.append("|---|---|---|---|---|---|")
    for r in tc_data:
        sev = str(r.get("Severity", "")).strip()
        sev_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢", "Info": "🔵"}.get(sev, "⚪")
        md.append(
            f"| `{escape(r.get('Test ID'))}` "
            f"| {escape(r.get('Component / Route'))} "
            f"| {escape(r.get('Control Area'))} "
            f"| {escape(r.get('Description / Vulnerability Audited'), 100)} "
            f"| {sev_emoji} {sev} "
            f"| {status_emoji(r.get('Verdict'))} |"
        )
    md.append("")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    md = []

    md.append("# 🧪 DairyDash — Full Test Reports Dashboard\n")
    md.append(f"_Generated: **{ts}**_\n")

    # Quick overview table
    md.append("## 📊 Reports Overview\n")
    md.append("| # | Report | File | Found |")
    md.append("|---|---|---|---|")
    entries = [
        ("📱", "Appium Mobile E2E (400)", "appium report.xlsx"),
        ("🌐", "Selenium Web E2E (400)", "selineum report.xlsx"),
        ("⚡", "Baseline Load Test PASS ONLY", "Baseline_Load_Test_PASS_ONLY_20260622_140125.xlsx"),
        ("🛡️", "Security Control Tests (400 v2)", "Security_Control_Test_Cases_Report_400_v2.xlsx"),
    ]
    for i, (emoji, name, fname) in enumerate(entries, 1):
        full = os.path.join(SCRIPT_DIR, fname)
        found = "✅ Yes" if os.path.isfile(full) else "❌ Missing"
        md.append(f"| {i} | {emoji} {name} | `{fname}` | {found} |")
    md.append("\n---\n")

    # Each report section
    section_appium(md)
    md.append("---\n")
    section_selenium(md)
    md.append("---\n")
    section_load(md)
    md.append("---\n")
    section_security(md)
    md.append("---\n")

    md.append("## 📦 Downloadable Artifacts")
    md.append("All 4 Excel reports are uploaded as downloadable artifacts — see the **Artifacts** section at the top of this page.\n")
    md.append(f"_Dashboard generated on {ts}_")

    full_md = "\n".join(md)

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(full_md + "\n")
        print(f"✅ Published full test case listing for all 4 reports to GitHub Step Summary!")
    else:
        print(full_md)

if __name__ == "__main__":
    main()
