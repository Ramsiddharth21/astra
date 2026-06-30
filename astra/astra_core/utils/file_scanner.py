import os

IGNORE_FOLDERS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".ruff_cache",
}

IGNORE_FILE_EXTENSIONS = {
    ".bak",
    ".log",
    ".json",
}


def scan_project_files(folder_path, extensions=(".py",)):
    collected_files = []

    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        for file in files:
            if any(file.endswith(ext) for ext in IGNORE_FILE_EXTENSIONS):
                continue

            if file.endswith(extensions):
                collected_files.append(os.path.join(root, file))

    return collected_files
