import subprocess


def run_runtime_fix(file_path):
    result = subprocess.run(
        ["python", file_path],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return None

    return result.stderr.strip()
