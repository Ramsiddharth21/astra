from astra_core.engines.python_engine import (
    python_autofix,
    python_format_black,
    python_lint,
    python_run_tests,
    python_sort_imports,
)
from astra_core.reports.report_generator import save_report
from astra_core.utils.permissions import ask_permission


def run_full_pipeline(folder_path):
    report = {"folder": folder_path, "steps": {}}

    # Step 1: Lint Before Fix
    lint_before = python_lint(folder_path)
    report["steps"]["lint_before"] = lint_before

    # Step 2: AutoFix
    if ask_permission("Apply Ruff autofix?"):
        autofix = python_autofix(folder_path)
        report["steps"]["ruff_autofix"] = autofix
    else:
        report["steps"]["ruff_autofix"] = {"skipped": True}

    # Step 3: isort
    if ask_permission("Apply import sorting (isort)?"):
        isort_result = python_sort_imports(folder_path)
        report["steps"]["isort"] = isort_result
    else:
        report["steps"]["isort"] = {"skipped": True}

    # Step 4: black formatting
    if ask_permission("Apply formatting (black)?"):
        black_result = python_format_black(folder_path)
        report["steps"]["black"] = black_result
    else:
        report["steps"]["black"] = {"skipped": True}

    # Step 5: Lint After Fix
    lint_after = python_lint(folder_path)
    report["steps"]["lint_after"] = lint_after

    # Step 6: Regression Testing
    if ask_permission("Run regression tests (pytest)?"):
        tests = python_run_tests(folder_path)
        report["steps"]["pytest"] = tests
    else:
        report["steps"]["pytest"] = {"skipped": True}

    report_file = save_report(report, filename="astra_report.json")
    return report_file
