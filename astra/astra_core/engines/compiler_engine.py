import subprocess


def python_compile_check(file_path):
    result = subprocess.run(
        ["python", "-m", "py_compile", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return None

    return result.stderr.strip()
