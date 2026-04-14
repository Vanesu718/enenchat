import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# simple regex to find createMsgElement function
match = re.search(r'function createMsgElement\([^)]*\)\s*\{(?:[^{}]*|\{(?:[^{}]*|\{[^{}]*\})*\})*\}', content)
if match:
    print(match.group(0))
else:
    print("Not found by simple regex, extracting line range")
    lines = content.split('\n')
    start = -1
    for i, line in enumerate(lines):
        if 'function createMsgElement(' in line:
            start = i
            break
    if start != -1:
        end = start
        braces = 0
        started = False
        for i in range(start, len(lines)):
            line = lines[i]
            if '{' in line:
                braces += line.count('{')
                started = True
            if '}' in line:
                braces -= line.count('}')
            if started and braces == 0:
                end = i
                break
        print('\n'.join(lines[start:end+1]))


