import os
import shutil


def create_backup(file_path):
    backup_path = file_path + ".bak"
    shutil.copy(file_path, backup_path)
    return backup_path


def restore_backup(file_path):
    backup_path = file_path + ".bak"

    if os.path.exists(backup_path):
        shutil.copy(backup_path, file_path)
        return True

    return False
