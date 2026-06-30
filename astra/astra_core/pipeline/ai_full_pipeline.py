from astra_core.engines.python_engine import (
    python_lint,
    python_autofix,
    python_format_black,
    python_sort_imports,
    python_run_tests,
)

from astra_core.pipeline.ai_compile_fix_pipeline import run_ai_compile_fix
from astra_core.pipeline.runtime_fix_pipeline import run_runtime_fix
from astra_core.reports.report_generator import save_report
from astra_core.utils.permissions import ask_permission


def run_full_pipeline_with_ai(folder_path):
    report = {"folder": folder_path, "steps": {}}

    lint_before = python_lint(folder_path)
    report["steps"]["lint_before"] = lint_before

    if ask_permission("Apply Ruff autofix?"):
        autofix = python_autofix(folder_path)
        report["steps"]["ruff_autofix"] = autofix
    else:
        report["steps"]["ruff_autofix"] = {"skipped": True}

    if ask_permission("Apply import sorting (isort)?"):
        isort_result = python_sort_imports(folder_path)
        report["steps"]["isort"] = isort_result
    else:
        report["steps"]["isort"] = {"skipped": True}

    if ask_permission("Apply formatting (black)?"):
        black_result = python_format_black(folder_path)
        report["steps"]["black"] = black_result
    else:
        report["steps"]["black"] = {"skipped": True}

    lint_after_fix = python_lint(folder_path)
    report["steps"]["lint_after_fix"] = lint_after_fix

    if ask_permission("Run AI Fix using compile check (syntax fixes)?"):
        compile_ai_report = run_ai_compile_fix(folder_path)
        report["steps"]["compile_ai_report"] = compile_ai_report
    else:
        report["steps"]["compile_ai_report"] = {"skipped": True}

    lint_after_compile_ai = python_lint(folder_path)
    report["steps"]["lint_after_compile_ai"] = lint_after_compile_ai

    if ask_permission("Run runtime execution fix (TypeError/NameError)?"):
        runtime_report = run_runtime_fix(folder_path)
        report["steps"]["runtime_fix"] = runtime_report
    else:
        report["steps"]["runtime_fix"] = {"skipped": True}

    lint_after_runtime = python_lint(folder_path)
    report["steps"]["lint_after_runtime"] = lint_after_runtime

    if ask_permission("Run regression tests (pytest)?"):
        tests = python_run_tests(folder_path)
        report["steps"]["pytest"] = tests
    else:
        report["steps"]["pytest"] = {"skipped": True}

    report_file = save_report(report, filename="astra_fullscan_ai_report.json")
    return report_file
