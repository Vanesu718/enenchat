import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find saveToStorage function
match = re.search(r'async function saveToStorage\(key, value\) \{.*?\n\}', content, re.DOTALL)
if match:
    print('=== saveToStorage ===')
    print(match.group()[:1500])
    print()

# Find getFromStorage function
match = re.search(r'async function getFromStorage\(key\) \{.*?\n\}', content, re.DOTALL)
if match:
    print('=== getFromStorage ===')
    print(match.group()[:1500])
    print()

# Find saveMomentsToDB function
match = re.search(r'async function saveMomentsToDB\(\) \{.*?\n\}', content, re.DOTALL)
if match:
    print('=== saveMomentsToDB ===')
    print(match.group()[:1500])
    print()

# Find loadMomentsFromDB function
match = re.search(r'async function loadMomentsFromDB\(\) \{.*?\n\}', content, re.DOTALL)
if match:
    print('=== loadMomentsFromDB ===')
    print(match.group()[:1500])
    print()

# Count all localStorage direct usages
ls_set = len(re.findall(r'localStorage\.setItem', content))
ls_get = len(re.findall(r'localStorage\.getItem', content))
ls_remove = len(re.findall(r'localStorage\.removeItem', content))
ls_clear = len(re.findall(r'localStorage\.clear', content))
print(f'=== localStorage direct usage ===')
print(f'setItem: {ls_set}')
print(f'getItem: {ls_get}')
print(f'removeItem: {ls_remove}')
print(f'clear: {ls_clear}')
print()

# Count IndexedDB usage
idb_save = len(re.findall(r'saveToStorage\(', content))
idb_get = len(re.findall(r'getFromStorage\(', content))
idb_mgr = len(re.findall(r'IndexedDBManager\.', content))
print(f'=== IndexedDB usage ===')
print(f'saveToStorage calls: {idb_save}')
print(f'getFromStorage calls: {idb_get}')
print(f'IndexedDBManager direct calls: {idb_mgr}')
print()

# Find localStorage usages that are NOT fallback/migration
print('=== localStorage.setItem locations (potential issues) ===')
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'localStorage.setItem' in line:
        context_start = max(0, i-2)
        context_end = min(len(lines), i+2)
        context = '\n'.join(lines[context_start:context_end])
        print(f'Line {i+1}:')
        print(context)
        print('---')
print()

print('=== localStorage.getItem locations (potential issues) ===')
for i, line in enumerate(lines):
    if 'localStorage.getItem' in line:
        # Skip if it's inside a migration or fallback context
        context_start = max(0, i-3)
        context_end = min(len(lines), i+2)
        context = '\n'.join(lines[context_start:context_end])
        print(f'Line {i+1}:')
        print(context)
        print('---')
