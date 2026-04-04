import os
import shutil
import time
from datetime import datetime

history_dir = r"C:\Users\Administrator\AppData\Roaming\Code\User\History"
dest_dir = r"c:\Users\Administrator\Desktop\111"

print("正在扫描VS Code本地缓存找回代码...")

if not os.path.exists(history_dir):
    print(f"找不到目录: {history_dir}")
    exit()

candidates = []
for root, _, files in os.walk(history_dir):
    for f in files:
        if f == 'entries.json':
            continue
        filepath = os.path.join(root, f)
        try:
            mtime = os.path.getmtime(filepath)
            # 只看最近24小时的文件
            if mtime > time.time() - 86400:
                candidates.append((mtime, filepath))
        except:
            pass

candidates.sort(reverse=True) # 最新的排前面

found_count = 0
for mtime, filepath in candidates:
    if found_count >= 5:
        break
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if "论坛" in content and "<html" in content and "面具" in content:
                recover_path = os.path.join(dest_dir, f"index_recovered_{found_count}.html")
                with open(recover_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(content)
                print(f"成功找到备份! 已恢复为 {recover_path}, 备份时间: {datetime.fromtimestamp(mtime)}")
                found_count += 1
    except Exception as e:
        pass

if found_count == 0:
    print("未能找到包含论坛和面具代码的备份。")
else:
    print("扫描完成。")
