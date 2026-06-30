def detect_language(file_path):
    if file_path.endswith(".py"):
        return "Python"
    elif file_path.endswith(".js"):
        return "JavaScript"
    elif file_path.endswith(".java"):
        return "Java"
    elif file_path.endswith(".cpp"):
        return "C++"
    elif file_path.endswith(".c"):
        return "C"
    elif file_path.endswith(".ts"):
        return "TypeScript"
    elif file_path.endswith(".go"):
        return "Go"
    else:
        return "Unknown"