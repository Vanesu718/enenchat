import os
import time

history_dir = r'C:\Users\Administrator\AppData\Roaming\Code\User\History'
all_files = []

for root, dirs, files in os.walk(history_dir):
    for f in files:
        if f != 'entries.json':
            full_path = os.path.join(root, f)
            all_files.append(full_path)

all_files.sort(key=os.path.getmtime, reverse=True)

for f in all_files[:30]:
    size = os.path.getsize(f)
    mtime = time.ctime(os.path.getmtime(f))
    print(f"{f} - {mtime} - {size} bytes")
