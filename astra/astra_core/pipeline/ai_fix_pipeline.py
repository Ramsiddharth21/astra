import os
import re

from astra_core.ai.ollama_engine import call_ollama
from astra_core.engines.python_engine import python_lint
from astra_core.reports.report_generator import save_report
from astra_core.utils.backup_manager import create_backup
from astra_core.utils.permissions import ask_permission


def extract_files_from_ruff_output(ruff_output, folder_path):
    files_found = set()

    # Handles format like:
    # --> file1.py:7:9
    arrow_pattern = r"-->\s+([^\s:]+\.py):\d+:\d+"
    matches = re.findall(arrow_pattern, ruff_output)

    for m in matches:
        file_path = os.path.join(folder_path, m)
        if os.path.exists(file_path):
            files_found.add(file_path)

    # Handles format like:
    # file1.py:7:9: F821 Undefined name `x`
    line_pattern = r"^([^\s:]+\.py):\d+:\d+"
    for line in ruff_output.splitlines():
        match = re.match(line_pattern, line.strip())
        if match:
            file_path = os.path.join(folder_path, match.group(1))
            if os.path.exists(file_path):
                files_found.add(file_path)

    return list(files_found)


def ai_fix_file(file_path, error_message, model="qwen2.5-coder:3b"):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    prompt = f"""
You are an expert software engineer.
Fix the following code based on the error message.
Return ONLY the corrected full code. No explanation.

ERROR MESSAGE:
{error_message}

FILE PATH:
{file_path}

CODE:
{code}
"""

    fixed_code = call_ollama(prompt, model=model)

    if not fixed_code.strip():
        return {"status": "failed", "reason": "Empty AI response"}

    print(f"\nAI fix suggestion generated for: {file_path}")

    if not ask_permission(f"Apply AI fix to {file_path}?"):
        return {"status": "skipped"}

    create_backup(file_path)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed_code)

    return {"status": "applied"}


def run_ai_fix_only(folder_path, model="qwen2.5-coder:3b"):
    lint_result = python_lint(folder_path)

    report = {
        "mode": "aifix",
        "folder": folder_path,
        "ruff_lint": lint_result,
        "ai_fixes": [],
    }

    # If already clean, no need to fix
    if lint_result["returncode"] == 0 and "All checks passed!" in lint_result["stdout"]:
        report_file = save_report(report, filename="astra_ai_report.json")
        return report_file

    combined_output = lint_result["stdout"] + "\n" + lint_result["stderr"]

    files_to_fix = extract_files_from_ruff_output(combined_output, folder_path)

    if not files_to_fix:
        report["note"] = "No files detected from ruff output for AI fixing."
        report_file = save_report(report, filename="astra_ai_report.json")
        return report_file

    for file_path in files_to_fix:
        result = ai_fix_file(file_path, combined_output, model=model)

        report["ai_fixes"].append(
            {"file": file_path, "error_context": combined_output, "result": result}
        )

    report_file = save_report(report, filename="astra_ai_report.json")
    return report_file
