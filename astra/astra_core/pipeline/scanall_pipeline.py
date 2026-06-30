import os
import subprocess
from astra_core.utils.file_scanner import scan_project_files
from astra_core.reports.report_generator import save_report


def compile_check(file_path):
    result = subprocess.run(
        ["python", "-m", "py_compile", file_path],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stderr.strip()


def ruff_check(file_path):
    result = subprocess.run(
        ["ruff", "check", file_path],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip()


def runtime_check(file_path):
    result = subprocess.run(
        ["python", file_path],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stderr.strip()


def scan_all(folder_path):
    files = scan_project_files(folder_path, extensions=(".py",))

    report = {
        "mode": "scanall",
        "folder": folder_path,
        "files_scanned": len(files),
        "files_with_errors": [],
    }

    for file_path in files:
        file_errors = []

        c_rc, c_err = compile_check(file_path)
        if c_rc != 0:
            file_errors.append({"type": "syntax", "error": c_err})

        r_rc, r_out = ruff_check(file_path)
        if r_rc != 0 and r_out:
            file_errors.append({"type": "ruff", "error": r_out})

        rt_rc, rt_err = runtime_check(file_path)
        if rt_rc != 0 and rt_err:
            file_errors.append({"type": "runtime", "error": rt_err})

        if file_errors:
            report["files_with_errors"].append(
                {"file": file_path, "errors": file_errors}
            )

    report_file = save_report(report, filename="astra_scanall_report.json")
    return report_file, report
