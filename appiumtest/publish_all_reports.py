import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import openpyxl
except ImportError:
    print("openpyxl not found, installing...")
    os.system("pip install openpyxl")
    import openpyxl

import datetime

# ── File Paths ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

REPORTS = {
    "appium":    os.path.join(SCRIPT_DIR, "appium report.xlsx"),
    "selenium":  os.path.join(SCRIPT_DIR, "selineum report.xlsx"),
    "load":      os.path.join(SCRIPT_DIR, "Baseline_Load_Test_PASS_ONLY_20260622_140125.xlsx"),
    "security":  os.path.join(SCRIPT_DIR, "Security_Control_Test_Cases_Report_400_v2.xlsx"),
}

# ── Generic helper: try to read first sheet and get basic stats ─────────────
def read_sheet_generic(filepath):
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return None, []
        headers = [str(c) if c is not None else "" for c in rows[0]]
        data = []
        for row in rows[1:]:
            if any(c is not None for c in row):
                data.append(dict(zip(headers, row)))
        return ws.title, data
    except Exception as e:
        return None, []

def count_status(data, col_hint="Status"):
    passed, failed, total = 0, 0, 0
    for row in data:
        val = ""
        for k, v in row.items():
            if col_hint.lower() in str(k).lower() and v is not None:
                val = str(v).strip().upper()
                break
        if val:
            total += 1
            if "PASS" in val or "PASSED" in val or val == "OK" or val == "SUCCESS":
                passed += 1
            elif "FAIL" in val or "FAILED" in val or val == "ERROR":
                failed += 1
    return total, passed, failed

def build_report_section(title, emoji, filepath, col_hint="Status"):
    lines = []
    if not os.path.isfile(filepath):
        lines.append(f"### {emoji} {title}")
        lines.append(f"> ⚠️ Report file not found: `{os.path.basename(filepath)}`\n")
        return lines

    sheet_name, data = read_sheet_generic(filepath)
    total, passed, failed = count_status(data, col_hint)
    skipped = total - passed - failed
    rate = f"{(passed/total*100):.1f}%" if total > 0 else "N/A"

    lines.append(f"### {emoji} {title}")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| 📄 File | `{os.path.basename(filepath)}` |")
    lines.append(f"| 📋 Sheet | `{sheet_name}` |")
    lines.append(f"| 🔢 Total Rows | **{len(data)}** |")
    if total > 0:
        lines.append(f"| ✅ Passed | **{passed}** |")
        lines.append(f"| ❌ Failed | **{failed}** |")
        if skipped > 0:
            lines.append(f"| ⏭️ Other | **{skipped}** |")
        lines.append(f"| 📈 Pass Rate | **{rate}** |")
    else:
        lines.append(f"| ℹ️ Note | No status column detected — row count shown |")
    lines.append("")

    # Collapsible detail table (first 30 rows max)
    if data:
        headers = list(data[0].keys())
        sample = data[:30]
        lines.append(f"<details><summary>🔍 Preview first {len(sample)} rows of {len(data)} total</summary>\n")
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")
        for row in sample:
            cells = []
            for h in headers:
                val = str(row.get(h, "")).replace("|", "\\|").replace("\n", " ")
                status_val = str(row.get(h, "")).strip().upper()
                if "PASS" in status_val and h.lower() in ("status", "result", "outcome"):
                    val = "✅ " + val
                elif "FAIL" in status_val and h.lower() in ("status", "result", "outcome"):
                    val = "❌ " + val
                cells.append(val[:80])
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("\n</details>\n")

    return lines

def main():
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    md = []
    md.append("# 🧪 DairyDash — Full Test Report Dashboard\n")
    md.append(f"_Generated at: **{ts}**_\n")
    md.append("---\n")

    # Overview Table
    md.append("## 📊 Reports Overview\n")
    md.append("| # | Report | File | Status |")
    md.append("|---|---|---|---|")
    for i, (key, path) in enumerate(REPORTS.items(), 1):
        exists = "✅ Found" if os.path.isfile(path) else "❌ Missing"
        md.append(f"| {i} | {key.capitalize()} | `{os.path.basename(path)}` | {exists} |")
    md.append("\n---\n")

    # Individual Sections
    md.extend(build_report_section(
        "Appium Mobile E2E Report (400 Cases)",
        "📱", REPORTS["appium"], col_hint="Status"
    ))
    md.append("---\n")

    md.extend(build_report_section(
        "Selenium Web E2E Report (400 Cases)",
        "🌐", REPORTS["selenium"], col_hint="Status"
    ))
    md.append("---\n")

    md.extend(build_report_section(
        "Baseline Load Test Report (PASS ONLY)",
        "⚡", REPORTS["load"], col_hint="Status"
    ))
    md.append("---\n")

    md.extend(build_report_section(
        "Security Control Test Cases Report (400 v2)",
        "🛡️", REPORTS["security"], col_hint="Result"
    ))
    md.append("---\n")

    md.append("## 📦 Downloadable Artifacts")
    md.append("All 4 Excel reports are uploaded as **downloadable artifacts** for this workflow run.")
    md.append("Click the **Artifacts** section at the top of this page to download them.\n")
    md.append(f"_Dashboard generated on {ts}_")

    full_md = "\n".join(md)

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(full_md + "\n")
        print("✅ Successfully published all 4 report summaries to GitHub Step Summary!")
    else:
        print(full_md)

if __name__ == "__main__":
    main()
