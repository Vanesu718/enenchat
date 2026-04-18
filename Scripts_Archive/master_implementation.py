#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master implementation script for all 5 steps of the modification plan.
Runs all changes in sequence.
"""

import os
import re
import shutil
import json
from datetime import datetime

BASE = r'c:\Users\Administrator\Desktop\111'
BACKUP_DIR = os.path.join(BASE, f'backup_master_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

def backup():
    """Step 1: Backup core files"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    files = ['js/main.js', 'index.html', 'css/chat.css', 'css/index-main.css', 'css/style.css', 'css/themes.css', 'css/moments.css']
    for f in files:
        src = os.path.join(BASE, f)
        if os.path.exists(src):
            dst = os.path.join(BACKUP_DIR, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  Backed up: {f}")
    print(f"Backup complete: {BACKUP_DIR}")

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {path}")

def modify_main_js():
    """Steps 2, 4, 5: Modify main.js"""
    path = os.path.join(BASE, 'js/main.js')
    content = read_file(path)
    original_len = len(content)
    
    changes_made = []
    
    # ==================
    # STEP 2A: 语言规范 → 世界观 (UI only - categories in worldbook)
    # ==================
    # Replace category name in worldbook filter tabs and dropdowns
    content_new = content.replace("'语言规范'", "'世界观'")
    content_new = content_new.replace('"语言规范"', '"世界观"')
    content_new = content_new.replace('语言规范', '世界观')
    if content_new != content:
        changes_made.append("2A: 语言规范→世界观")
        content = content_new

    # ==================
    # STEP 2B: Add 其他 category to worldbook
    # ==================
    # Find worldbook categories array and add 其他
    # Pattern: categories like ['记忆总结', '世界观'] or similar
    patterns_to_try = [
        (r"(const\s+worldbookCategories\s*=\s*\[)([^\]]*?)(记忆总结[^\]]*?)(\])", None),
    ]
    
    # Search for worldbook category definitions
    cat_match = re.search(r"(categories\s*[=:]\s*\[)(.*?记忆总结.*?)(\])", content, re.DOTALL)
    if cat_match:
        cat_content = cat_match.group(2)
        if '其他' not in cat_content and '世界观' in cat_content:
            new_cat = cat_match.group(1) + cat_content.rstrip().rstrip(',') + ", '其他'" + cat_match.group(3)
            content = content[:cat_match.start()] + new_cat + content[cat_match.end():]
            changes_made.append("2B: Added 其他 category")

    # Also look for worldbook filter tab rendering
    # Find where tabs are rendered for worldbook categories
    tab_pattern = r"(全部.*?记忆总结.*?)(世界观|语言规范)(.*?)(</.*?>|'|\")"
    
    # ==================
    # STEP 2C: Fix 记忆总结 trigger logic
    # ==================
    # Find where worldbook entries are injected into context
    # 记忆总结 should only inject if contact has it explicitly enabled
    
    # Look for the memory/worldbook injection logic
    # Pattern: entries with type 记忆总结 being added to all contacts
    inject_pattern = re.search(
        r"(// .*?世界书|worldbook.*?inject|inject.*?worldbook)(.*?)(记忆总结)(.*?)(forEach|map|filter)",
        content, re.DOTALL | re.IGNORECASE
    )
    
    # Search for where worldbook entries get added to messages
    # Find the function that builds the system prompt / context
    build_context_match = re.search(
        r"(function\s+\w*[Cc]ontext\w*\s*\([^)]*\)|function\s+\w*[Ss]ystem\w*\s*\([^)]*\)|function\s+\w*[Pp]rompt\w*\s*\([^)]*\))",
        content
    )
    
    # Find worldbook entry filtering for 记忆总结
    # The key fix: 记忆总结 entries should check if the contact has explicitly opted in
    # Look for keyword-based filtering
    keyword_inject = re.search(
        r"(entry\.type\s*===\s*['\"]记忆总结['\"]|['\"]记忆总结['\"]\s*===\s*entry\.type)(.*?)(return true|push\(entry\)|always|global)",
        content, re.DOTALL
    )
    
    changes_made.append("2C: Will apply 记忆总结 fix")
    
    # ==================
    # STEP 4 & 5 additions: Writing Style
    # ==================
    
    # Check if writingStyleEntries already exists
    if 'writingStyleEntries' not in content:
        changes_made.append("Need to add writingStyleEntries")
    
    if 'compressedStyle' not in content:
        changes_made.append("Need to add compressedStyle logic")
    
    print(f"  Changes identified: {changes_made}")
    print(f"  Content length: {original_len} -> {len(content)}")
    
    write_file(path, content)
    return changes_made

def analyze_worldbook_structure():
    """Analyze the current worldbook structure to understand what changes are needed"""
    path = os.path.join(BASE, 'js/main.js')
    content = read_file(path)
    
    # Find worldbook-related code sections
    results = {}
    
    # Find category definitions
    lines = content.split('\n')
    worldbook_lines = []
    for i, line in enumerate(lines):
        if any(kw in line for kw in ['worldBook', 'WorldBook', 'world_book', 'worldbook', '世界书', '记忆总结', '语言规范', '世界观', 'writingStyle', '文风']):
            worldbook_lines.append((i+1, line))
    
    results['worldbook_lines'] = worldbook_lines[:50]  # First 50 matches
    
    # Save analysis
    analysis_path = os.path.join(BASE, 'worldbook_analysis.txt')
    with open(analysis_path, 'w', encoding='utf-8') as f:
        f.write("=== WORLDBOOK STRUCTURE ANALYSIS ===\n\n")
        f.write("Lines containing worldbook/style keywords:\n")
        for lineno, line in worldbook_lines:
            f.write(f"L{lineno}: {line.strip()}\n")
    
    print(f"Analysis saved to: {analysis_path}")
    print(f"Found {len(worldbook_lines)} relevant lines")
    
    # Also find writing style related
    style_lines = []
    for i, line in enumerate(lines):
        if any(kw in line for kw in ['writingStyle', 'writing_style', '文风', 'compressedStyle', 'styleEntry']):
            style_lines.append((i+1, line))
    
    print(f"Found {len(style_lines)} writing style lines")
    
    return content, lines, worldbook_lines, style_lines

def get_context_around_line(lines, lineno, context=20):
    """Get lines around a specific line number"""
    start = max(0, lineno - context - 1)
    end = min(len(lines), lineno + context)
    result = []
    for i in range(start, end):
        result.append(f"L{i+1}: {lines[i]}")
    return '\n'.join(result)

def main():
    print("=" * 60)
    print("MASTER IMPLEMENTATION SCRIPT")
    print("=" * 60)
    
    print("\n[STEP 1] Creating backup...")
    backup()
    
    print("\n[ANALYSIS] Analyzing worldbook structure...")
    content, lines, wb_lines, style_lines = analyze_worldbook_structure()
    
    print("\nFirst 20 worldbook-related lines:")
    for lineno, line in wb_lines[:20]:
        print(f"  L{lineno}: {line.strip()[:100]}")
    
    print("\nExiting for analysis - please review worldbook_analysis.txt")
    print("Then run the targeted fix scripts.")

if __name__ == '__main__':
    main()
