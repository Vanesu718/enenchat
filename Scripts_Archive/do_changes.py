#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master change script - implements all 5 steps of the modification plan
"""

import os
import shutil
import re
import json
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'

def backup():
    """Step 1: Backup core files"""
    backup_dir = os.path.join(BASE, f'backup_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'css'), exist_ok=True)
    
    files = [
        'js/main.js', 'index.html',
        'css/chat.css', 'css/index-main.css', 'css/style.css', 'css/themes.css'
    ]
    for f in files:
        src = os.path.join(BASE, f)
        dst = os.path.join(backup_dir, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f'  Backed up: {f}')
    print(f'Backup complete: {backup_dir}')
    return backup_dir

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def scan_main_js():
    """Scan main.js for relevant patterns"""
    path = os.path.join(BASE, 'js', 'main.js')
    content = read_file(path)
    lines = content.split('\n')
    
    patterns = ['语言规范', '记忆总结', '世界书', 'worldbook', 'worldBook', 'world_book', 
                '文风', 'writingStyle', 'writing_style', 'chatSetting', 'chat-setting']
    
    results = {}
    for pat in patterns:
        found = []
        for i, line in enumerate(lines):
            if pat.lower() in line.lower() or pat in line:
                found.append((i+1, line.rstrip()))
        if found:
            results[pat] = found
    
    return content, lines, results

def main():
    print("="*60)
    print("Master Change Script - All 5 Steps")
    print("="*60)
    
    # Step 1: Backup
    print("\n[Step 1] Backing up files...")
    backup()
    
    # Step 2: Scan main.js
    print("\n[Scanning main.js for patterns...]")
    main_js_path = os.path.join(BASE, 'js', 'main.js')
    content, lines, results = scan_main_js()
    
    print(f"Total lines in main.js: {len(lines)}")
    for pat, occurrences in results.items():
        print(f"\n  Pattern '{pat}' found {len(occurrences)} times:")
        for lineno, line in occurrences[:5]:
            print(f"    Line {lineno}: {line[:100]}")
    
    # Save scan results
    scan_output = []
    scan_output.append(f"main.js has {len(lines)} lines\n")
    for pat, occurrences in results.items():
        scan_output.append(f"\nPattern '{pat}' ({len(occurrences)} occurrences):")
        for lineno, line in occurrences:
            scan_output.append(f"  L{lineno}: {line[:120]}")
    
    with open(os.path.join(BASE, 'scan_results.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(scan_output))
    print("\nScan results saved to scan_results.txt")
    
    # Also scan index.html
    print("\n[Scanning index.html for patterns...]")
    html_path = os.path.join(BASE, 'index.html')
    html_content = read_file(html_path)
    html_lines = html_content.split('\n')
    
    html_results = {}
    for pat in ['语言规范', '记忆总结', '世界书', 'worldbook', '文风', 'writingStyle', 
                '通讯录', 'contacts-menu', 'chat-settings', 'chatSettings']:
        found = []
        for i, line in enumerate(html_lines):
            if pat.lower() in line.lower() or pat in line:
                found.append((i+1, line.rstrip()))
        if found:
            html_results[pat] = found
    
    print(f"Total lines in index.html: {len(html_lines)}")
    for pat, occurrences in html_results.items():
        print(f"\n  Pattern '{pat}' found {len(occurrences)} times:")
        for lineno, line in occurrences[:5]:
            print(f"    Line {lineno}: {line[:100]}")
    
    html_scan = []
    html_scan.append(f"index.html has {len(html_lines)} lines\n")
    for pat, occurrences in html_results.items():
        html_scan.append(f"\nPattern '{pat}' ({len(occurrences)} occurrences):")
        for lineno, line in occurrences:
            html_scan.append(f"  L{lineno}: {line[:120]}")
    
    with open(os.path.join(BASE, 'scan_html_results.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_scan))
    print("\nHTML scan results saved to scan_html_results.txt")

if __name__ == '__main__':
    main()
