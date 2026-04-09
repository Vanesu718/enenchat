#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master implementation script for all changes.
Runs as a standalone Python script to avoid context window issues.
"""

import re
import shutil
import os
import json
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'

def backup():
    """Step 1: Create backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(BASE, f'backup_master_{timestamp}')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'css'), exist_ok=True)
    
    files = [
        ('js/main.js', 'js/main.js'),
        ('index.html', 'index.html'),
        ('css/style.css', 'css/style.css'),
        ('css/chat.css', 'css/chat.css'),
        ('css/index-main.css', 'css/index-main.css'),
    ]
    for src, dst in files:
        src_path = os.path.join(BASE, src)
        dst_path = os.path.join(backup_dir, dst)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f'  Backed up: {src}')
    print(f'Backup complete: {backup_dir}')
    return True

def read_file(path):
    with open(os.path.join(BASE, path), 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(os.path.join(BASE, path), 'w', encoding='utf-8') as f:
        f.write(content)

def scan_main_js():
    """Scan main.js for key function/section locations"""
    content = read_file('js/main.js')
    lines = content.split('\n')
    
    keywords = [
        'worldBookEntries',
        'WORLDBOOK_ENTRIES',
        'writingStyle',
        'WRITING_STYLE',
        'worldbook-category-filter',
        'renderWorldBook',
        'openWorldBookEditor',
        'saveWorldBookEntry',
        'getContactWorldBookPrompt',
        'selectedWorldBooks',
        '记忆总结',
        '语言规范',
        '世界观',
        'category',
        'openChatSettings',
        'saveChatSettings',
        'chatSettings',
        'compressedStyle',
        'writingStyleEntries',
        'WRITING_STYLE_ENTRIES',
        'renderWritingStyles',
        'openWritingStyleEditor',
        'chat-setting',
        'useWorldBook',
        'selectedWorldBook',
        'triggerType',
        'keyword',
    ]
    
    print("=== Scanning main.js for key terms ===")
    for kw in keywords:
        found_lines = []
        for i, line in enumerate(lines):
            if kw in line:
                found_lines.append(i+1)
        if found_lines:
            print(f"  '{kw}': lines {found_lines[:5]}")
        else:
            print(f"  '{kw}': NOT FOUND")
    
    return content, lines

def scan_index_html():
    """Scan index.html for key sections"""
    content = read_file('index.html')
    lines = content.split('\n')
    
    keywords = [
        'worldbook-category-filter',
        'worldbook-tab',
        '世界书',
        '语言规范',
        '世界观',
        '记忆总结',
        '文风设置',
        'writing-style',
        'chat-setting',
        'useWorldBook',
        '通讯录',
        'contacts-menu',
        'nav-item',
        'writingStyle',
    ]
    
    print("\n=== Scanning index.html for key terms ===")
    for kw in keywords:
        found_lines = []
        for i, line in enumerate(lines):
            if kw in line:
                found_lines.append(i+1)
        if found_lines:
            print(f"  '{kw}': lines {found_lines[:5]}")
        else:
            print(f"  '{kw}': NOT FOUND")

if __name__ == '__main__':
    print("=== Master Plan Scanner ===\n")
    print("Step 1: Creating backup...")
    backup()
    
    print("\nStep 2: Scanning files...")
    content, lines = scan_main_js()
    scan_index_html()
    
    print("\n=== Done scanning. Now showing key code sections ===\n")
    
    # Show worldbook-related sections around line 270-320 area
    # Find getContactWorldBookPrompt function
    for i, line in enumerate(lines):
        if 'getContactWorldBookPrompt' in line and 'async function' in line:
            print(f"\n--- getContactWorldBookPrompt function (line {i+1}) ---")
            for j in range(i, min(i+30, len(lines))):
                print(f"{j+1}: {lines[j]}")
            break
    
    # Find worldbook rendering
    for i, line in enumerate(lines):
        if 'renderWorldBook' in line and 'function' in line:
            print(f"\n--- renderWorldBook function (line {i+1}) ---")
            for j in range(i, min(i+50, len(lines))):
                print(f"{j+1}: {lines[j]}")
            break
    
    # Find openChatSettings
    for i, line in enumerate(lines):
        if 'function openChatSettings' in line or 'openChatSettings' in line and 'async function' in line:
            print(f"\n--- openChatSettings function (line {i+1}) ---")
            for j in range(i, min(i+80, len(lines))):
                print(f"{j+1}: {lines[j]}")
            break
    
    # Find saveChatSettings
    for i, line in enumerate(lines):
        if 'function saveChatSettings' in line or ('saveChatSettings' in line and 'function' in line):
            print(f"\n--- saveChatSettings function (line {i+1}) ---")
            for j in range(i, min(i+60, len(lines))):
                print(f"{j+1}: {lines[j]}")
            break
    
    # Find the worldbook category filter tabs in JS (renderWorldBookTabs or similar)
    for i, line in enumerate(lines):
        if ('语言规范' in line or '记忆总结' in line) and i > 200:
            print(f"\n--- Near line {i+1} (category reference) ---")
            for j in range(max(0,i-5), min(i+10, len(lines))):
                print(f"{j+1}: {lines[j]}")
    
    # Find where messages are sent to AI (buildPrompt or similar)
    for i, line in enumerate(lines):
        if 'buildPrompt' in line and 'function' in line:
            print(f"\n--- buildPrompt function (line {i+1}) ---")
            for j in range(i, min(i+100, len(lines))):
                print(f"{j+1}: {lines[j]}")
            break
    
    # Also look for sendMessage or the AI call
    for i, line in enumerate(lines):
        if 'async function sendMessage' in line or 'function sendMessage' in line:
            print(f"\n--- sendMessage function (line {i+1}) ---")
            for j in range(i, min(i+50, len(lines))):
                print(f"{j+1}: {lines[j]}")
            break

print("\n=== Scan complete ===")
