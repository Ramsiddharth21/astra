import subprocess


def call_ollama(prompt, model="qwen2.5-coder:3b"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return ""

        return result.stdout.strip()

    except Exception:
        return ""
