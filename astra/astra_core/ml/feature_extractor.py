import ast


def extract_features(code: str):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "loc": len(code.splitlines()),
            "complexity": 999,
            "num_functions": 0,
            "num_imports": 0,
            "num_loops": 0,
            "num_conditions": 0,
            "num_try": 0,
            "num_classes": 0,
        }

    num_functions = 0
    num_imports = 0
    num_loops = 0
    num_conditions = 0
    num_try = 0
    num_classes = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            num_functions += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            num_imports += 1
        elif isinstance(node, (ast.For, ast.While)):
            num_loops += 1
        elif isinstance(node, ast.If):
            num_conditions += 1
        elif isinstance(node, ast.Try):
            num_try += 1
        elif isinstance(node, ast.ClassDef):
            num_classes += 1

    loc = len(code.splitlines())

    complexity = num_loops + num_conditions + num_try + num_functions + num_classes

    return {
        "loc": loc,
        "complexity": complexity,
        "num_functions": num_functions,
        "num_imports": num_imports,
        "num_loops": num_loops,
        "num_conditions": num_conditions,
        "num_try": num_try,
        "num_classes": num_classes,
    }
