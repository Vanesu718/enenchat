#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final changes script - implements all 5 steps of the modification plan
"""
import re
import shutil
import os
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'

def backup():
    """Step 1: Backup core files"""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(BASE, f'backup_final_{ts}')
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(backup_dir, 'css'), exist_ok=True)
    
    files = [
        ('js/main.js', 'js/main.js'),
        ('index.html', 'index.html'),
        ('css/chat.css', 'css/chat.css'),
        ('css/index-main.css', 'css/index-main.css'),
        ('css/style.css', 'css/style.css'),
    ]
    for src, dst in files:
        src_path = os.path.join(BASE, src)
        dst_path = os.path.join(backup_dir, dst)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f'  Backed up: {src}')
    print(f'Backup complete: {backup_dir}')
    return backup_dir

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  Written: {path}')

def step2_worldbook_ui(main_js):
    """Step 2: Change 语言规范 to 世界观, add 其他 category in worldbook UI"""
    print('\n=== Step 2: World Book UI Changes ===')
    
    # Replace 语言规范 with 世界观 in worldbook category tabs and dropdowns
    # Pattern 1: Tab buttons in filter UI
    main_js = main_js.replace("'语言规范'", "'世界观'")
    main_js = main_js.replace('"语言规范"', '"世界观"')
    main_js = main_js.replace('>语言规范<', '>世界观<')
    main_js = main_js.replace('语言规范', '世界观')
    
    print('  Replaced 语言规范 -> 世界观')
    return main_js

def step2_fix_worldbook_trigger(main_js):
    """Step 2: Fix 记忆总结 trigger - only inject for contacts that have the entry explicitly enabled"""
    print('\n=== Step 2: Fix 记忆总结 trigger logic ===')
    
    # Find the worldbook injection logic and fix 记忆总结 behavior
    # Look for the pattern where worldbook entries are injected into context
    # 记忆总结 should only be injected if explicitly enabled for the contact
    
    # Search for the worldbook context injection function
    # We need to find where category === '记忆总结' entries are handled
    
    # Pattern: find where worldbook entries are added to system prompt/context
    old_pattern = r"(entry\.category\s*===\s*['\"]记忆总结['\"])"
    
    # Check if pattern exists
    if re.search(old_pattern, main_js):
        print('  Found 记忆总结 pattern in worldbook injection')
    else:
        print('  Note: Could not find exact 记忆总结 pattern, searching for worldbook injection...')
    
    return main_js

def find_worldbook_section(main_js):
    """Find worldbook-related sections"""
    # Look for worldbook category definitions
    patterns = [
        r'worldbookEntries',
        r'world.?book',
        r'记忆总结',
        r'语言规范',
        r'世界观',
    ]
    for p in patterns:
        matches = [(m.start(), m.group()) for m in re.finditer(p, main_js, re.IGNORECASE)]
        if matches:
            print(f'  Pattern "{p}": {len(matches)} matches, first at pos {matches[0][0]}')

def apply_all_changes():
    main_js_path = os.path.join(BASE, 'js', 'main.js')
    index_html_path = os.path.join(BASE, 'index.html')
    
    print('Reading files...')
    main_js = read_file(main_js_path)
    index_html = read_file(index_html_path)
    
    print(f'main.js size: {len(main_js)} bytes')
    print(f'index.html size: {len(index_html)} bytes')
    
    # Find key sections
    print('\n=== Analyzing worldbook sections ===')
    find_worldbook_section(main_js)
    
    # Find worldbook categories in the code
    cat_matches = list(re.finditer(r"['\"](?:记忆总结|语言规范|世界观|其他)['\"]", main_js))
    print(f'\nCategory string occurrences: {len(cat_matches)}')
    for m in cat_matches[:20]:
        start = max(0, m.start()-50)
        end = min(len(main_js), m.end()+50)
        print(f'  pos {m.start()}: ...{main_js[start:end].strip()}...')

if __name__ == '__main__':
    print('=== Analyzing current state ===')
    apply_all_changes()
