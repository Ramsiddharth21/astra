def ask_permission(message):
    choice = input(f"{message} (y/n): ").strip().lower()
    return choice == "y"
