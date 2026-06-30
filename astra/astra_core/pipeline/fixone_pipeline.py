import subprocess

from astra_core.ai.ollama_engine import call_ollama
from astra_core.utils.backup_manager import create_backup, restore_backup
from astra_core.utils.permissions import ask_permission


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


def clean_ai_output(ai_text: str) -> str:
    if not ai_text:
        return ""

    cleaned = ai_text.strip()

    # Remove markdown fences if present
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```python", "")
        cleaned = cleaned.replace("```py", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

    # Remove useless starting words like "python"
    lines = cleaned.splitlines()

    while lines and lines[0].strip().lower() in ["python", "py", "code"]:
        lines.pop(0)

    cleaned = "\n".join(lines).strip()

    return cleaned


def is_valid_python_code(text: str) -> bool:
    if not text.strip():
        return False

    # basic check (must contain def/class/import or normal python statements)
    if (
        "def " not in text
        and "class " not in text
        and "import " not in text
        and "from " not in text
        and "print(" not in text
    ):
        return False

    return True


def fix_one_file(file_path, model="qwen2.5-coder:3b", max_attempts=5):
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    error_context = ""

    c_rc, c_err = compile_check(file_path)
    if c_rc != 0:
        error_context += "\nSYNTAX ERROR:\n" + c_err + "\n"

    r_rc, r_out = ruff_check(file_path)
    if r_rc != 0:
        error_context += "\nRUFF ERROR:\n" + r_out + "\n"

    rt_rc, rt_err = runtime_check(file_path)
    if rt_rc != 0:
        error_context += "\nRUNTIME ERROR:\n" + rt_err + "\n"

    if not error_context.strip():
        return {"status": "clean", "message": "No errors detected"}

    print("\nErrors found in:", file_path)
    print(error_context)

    if not ask_permission("Apply AI fixes to this file?"):
        return {"status": "skipped", "message": "User skipped fix"}

    create_backup(file_path)

    for attempt in range(1, max_attempts + 1):
        print(f"\nFix attempt {attempt} for: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            current_code = f.read()

        prompt = f"""
You are an expert Python developer.
Fix the following code completely.

RULES:
- Return ONLY corrected full Python code.
- Do NOT include markdown.
- Do NOT include explanations.
- Do NOT include comments like "here is the fixed code".
- Output must be directly runnable Python.

ERROR CONTEXT:
{error_context}

CODE:
{current_code}
"""

        fixed_code = call_ollama(prompt, model=model)

        fixed_code = clean_ai_output(fixed_code)

        if not fixed_code.strip():
            restore_backup(file_path)
            return {"status": "failed", "reason": "Empty AI output"}

        if not is_valid_python_code(fixed_code):
            restore_backup(file_path)
            return {"status": "failed", "reason": "AI output is not valid python code"}

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # Validate again after writing
        c2_rc, c2_err = compile_check(file_path)
        if c2_rc != 0:
            error_context = "\nSYNTAX ERROR:\n" + c2_err + "\n"
            continue

        r2_rc, r2_out = ruff_check(file_path)
        if r2_rc != 0:
            error_context = "\nRUFF ERROR:\n" + r2_out + "\n"
            continue

        rt2_rc, rt2_err = runtime_check(file_path)
        if rt2_rc != 0:
            error_context = "\nRUNTIME ERROR:\n" + rt2_err + "\n"
            continue

        return {"status": "applied", "message": f"File fixed successfully in {attempt} attempts"}

    restore_backup(file_path)
    return {
        "status": "rollback",
        "reason": "Max attempts reached, file still has errors",
        "message": f"Restored backup after {max_attempts} failed attempts",
    }
