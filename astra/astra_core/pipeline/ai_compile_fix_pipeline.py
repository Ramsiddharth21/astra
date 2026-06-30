from astra_core.ai.ollama_engine import call_ollama
from astra_core.engines.compiler_engine import python_compile_check
from astra_core.engines.python_engine import run_command
from astra_core.reports.report_generator import save_report
from astra_core.utils.backup_manager import create_backup, restore_backup
from astra_core.utils.file_scanner import scan_project_files
from astra_core.utils.permissions import ask_permission


def ruff_check_file(file_path):
    return run_command(["ruff", "check", file_path])


def ai_fix_file(file_path, error_context, model="qwen2.5-coder:3b"):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    prompt = f"""
You are an expert Python engineer.
Fix the following code.
Return ONLY corrected full code. No explanation.

ERROR CONTEXT:
{error_context}

CODE:
{code}
"""

    fixed_code = call_ollama(prompt, model=model)

    if not fixed_code.strip():
        return None

    return fixed_code


def run_ai_compile_fix(folder_path, model="qwen2.5-coder:3b"):
    files = scan_project_files(folder_path, extensions=(".py",))

    report = {
        "mode": "ai_compile_fix",
        "folder": folder_path,
        "files_checked": len(files),
        "fixes": [],
    }

    for file_path in files:
        compile_result = python_compile_check(file_path)

        if compile_result["returncode"] != 0:
            print(f"\nSyntax issue detected in: {file_path}")
            print(compile_result["stderr"])

            if not ask_permission(f"AI fix syntax errors in {file_path}?"):
                report["fixes"].append(
                    {"file": file_path, "status": "skipped_syntax_fix"}
                )
                continue

            create_backup(file_path)

            fixed_code = ai_fix_file(file_path, compile_result["stderr"], model=model)

            if not fixed_code:
                restore_backup(file_path)
                report["fixes"].append(
                    {"file": file_path, "status": "failed", "reason": "Empty AI output"}
                )
                continue

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)

            # Validate compile again
            compile_again = python_compile_check(file_path)

            if compile_again["returncode"] != 0:
                restore_backup(file_path)
                report["fixes"].append(
                    {
                        "file": file_path,
                        "status": "rollback",
                        "reason": "Still failing compile",
                        "error_after": compile_again["stderr"],
                    }
                )
                continue

            # Now validate with Ruff (logical/static)
            ruff_result = ruff_check_file(file_path)

            if ruff_result["returncode"] != 0:
                print(f"\nRuff issues still found in: {file_path}")
                print(ruff_result["stdout"])

                if ask_permission("Run AI again to fix Ruff issues?"):
                    fixed_code_2 = ai_fix_file(file_path, ruff_result["stdout"], model=model)

                    if fixed_code_2:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(fixed_code_2)

                        # Final Ruff validation
                        ruff_again = ruff_check_file(file_path)

                        if ruff_again["returncode"] != 0:
                            restore_backup(file_path)
                            report["fixes"].append(
                                {
                                    "file": file_path,
                                    "status": "rollback",
                                    "reason": "AI could not fix Ruff errors",
                                    "ruff_after": ruff_again["stdout"],
                                }
                            )
                            continue
                    else:
                        restore_backup(file_path)
                        report["fixes"].append(
                            {
                                "file": file_path,
                                "status": "rollback",
                                "reason": "Second AI fix empty",
                            }
                        )
                        continue

            report["fixes"].append(
                {"file": file_path, "status": "applied", "validated": True}
            )

    report_file = save_report(report, filename="astra_ai_compile_report.json")
    return report_file
