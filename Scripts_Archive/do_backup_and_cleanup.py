import os
import shutil
import datetime

backup_record_dir = "备份记录"
if not os.path.exists(backup_record_dir):
    os.makedirs(backup_record_dir)

# Old backups to move
items_to_move = [
    "backup_before_auto_summary",
    "backup_before_auto_summary_ui",
    "backup_before_deleting_scene_setting",
    "backup_before_prompt_fix",
    "backup_before_streaming",
    "backup_prompt_fix_2",
    "backup_all_code_20260409.zip"
]

for item in items_to_move:
    if os.path.exists(item):
        dest = os.path.join(backup_record_dir, item)
        if not os.path.exists(dest):
            try:
                shutil.move(item, dest)
                print(f"Moved {item} to {backup_record_dir}/")
            except Exception as e:
                print(f"Failed to move {item}: {e}")

# Create new backup
timestamp = datetime.datetime.now().strftime("%Y%md%H%M")
new_backup_dir = os.path.join(backup_record_dir, f"backup_{timestamp}")
os.makedirs(new_backup_dir)

# Files to backup
files_to_backup = [
    "index.html",
    "js",
    "css",
    "ICON"
]

for item in files_to_backup:
    if os.path.exists(item):
        dest = os.path.join(new_backup_dir, item)
        try:
            if os.path.isdir(item):
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)
            print(f"Backed up {item} to {new_backup_dir}/")
        except Exception as e:
            print(f"Failed to backup {item}: {e}")

print("Backup and cleanup completed.")
