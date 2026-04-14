#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Master implementation script for all 5 steps"""

import os
import re
import shutil
import datetime

BASE = r'c:\Users\Administrator\Desktop\111'
MAIN_JS = os.path.join(BASE, 'js', 'main.js')
INDEX_HTML = os.path.join(BASE, 'index.html')

# Step 1: Backup
def backup():
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(BASE, f'backup_final_{ts}')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'css'), exist_ok=True)
    shutil.copy2(MAIN_JS, os.path.join(backup_dir, 'js', 'main.js'))
    shutil.copy2(INDEX_HTML, os.path.join(backup_dir, 'index.html'))
    for f in os.listdir(os.path.join(BASE, 'css')):
        shutil.copy2(os.path.join(BASE, 'css', f), os.path.join(backup_dir, 'css', f))
    print(f'✅ Backup done: {backup_dir}')
    return backup_dir

# Read main.js
def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ Written: {path}')

def analyze_main():
    content = read_file(MAIN_JS)
    lines = content.split('\n')
    keywords = ['语言规范', '记忆总结', 'writingStyle', '文风', 'worldbook-category', 
                '世界观', 'selectedWorldBooks', 'privateSettings', 'compressedStyle',
                'worldBookEntries', 'category']
    
    print(f'\n=== main.js analysis ({len(lines)} lines) ===')
    for kw in keywords:
        matches = [(i+1, lines[i].strip()) for i in range(len(lines)) if kw in lines[i]]
        if matches:
            print(f'\n--- {kw} ({len(matches)} occurrences) ---')
            for ln, text in matches[:5]:
                print(f'  Line {ln}: {text[:100]}')
    
    # Find worldbook-related HTML sections in index.html
    html_content = read_file(INDEX_HTML)
    html_lines = html_content.split('\n')
    print(f'\n=== index.html analysis ({len(html_lines)} lines) ===')
    html_kw = ['worldbook-category', '语言规范', '文风', 'writingStyle', 'worldbook-menu', 
               'worldbook', '记忆总结']
    for kw in html_kw:
        matches = [(i+1, html_lines[i].strip()) for i in range(len(html_lines)) if kw in html_lines[i]]
        if matches:
            print(f'\n--- {kw} ({len(matches)} occurrences) ---')
            for ln, text in matches[:8]:
                print(f'  Line {ln}: {text[:120]}')

if __name__ == '__main__':
    backup()
    analyze_main()
