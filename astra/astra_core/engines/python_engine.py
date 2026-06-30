import subprocess


def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def python_lint(folder_path):
    return run_command(["ruff", "check", folder_path])


def python_autofix(folder_path):
    return run_command(["ruff", "check", folder_path, "--fix"])


def python_format_black(folder_path):
    return run_command(["black", folder_path])


def python_sort_imports(folder_path):
    return run_command(["isort", folder_path])


def python_run_tests(folder_path):
    return run_command(["pytest", folder_path])
