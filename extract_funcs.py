import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

funcs = []

# Extract processOnlineResponse
m = re.search(r'async function processOnlineResponse\([\s\S]*?\n\}', content)
if m:
    funcs.append(m.group(0))

# Extract handleReRoll
m2 = re.search(r'async function handleReRoll\([\s\S]*?\n\}', content)
if not m2:
    m2 = re.search(r'window\.handleReRoll\s*=\s*async\s*function\s*\([\s\S]*?\n\}', content)
if m2:
    funcs.append(m2.group(0))

# Extract triggerAIReply
# We need to handle nested braces, so simple regex might fail. 
# Let's just grab the whole function based on known structure or use a simple brace counter.

def extract_function(name):
    idx = content.find(f'async function {name}(')
    if idx == -1:
        idx = content.find(f'function {name}(')
        if idx == -1:
            idx = content.find(f'{name}: function')
            if idx == -1:
                return f"{name} not found"
    
    start_brace = content.find('{', idx)
    brace_count = 1
    i = start_brace + 1
    while brace_count > 0 and i < len(content):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
        i += 1
    return content[idx:i]

with open('extracted_funcs.txt', 'w', encoding='utf-8') as f:
    f.write(extract_function('triggerAIReply'))
    f.write('\n\n')
    f.write(extract_function('handleReRoll'))
    f.write('\n\n')
    f.write(extract_function('processOnlineResponse'))
