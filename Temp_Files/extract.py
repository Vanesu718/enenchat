import re

def extract_func(filepath, func_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'(?:async\s+)?function\s+' + func_name + r'\s*\('
    match = re.search(pattern, content)
    if not match:
        print(f"{func_name} not found")
        return
    
    start = match.start()
    
    # Find the first '{' after the function declaration
    brace_start = content.find('{', start)
    if brace_start == -1:
        return
        
    brace_count = 0
    in_string = False
    string_char = ''
    in_comment = False
    in_multiline_comment = False
    
    i = brace_start
    while i < len(content):
        char = content[i]
        
        if not in_string and not in_comment and not in_multiline_comment:
            if char == '/' and i + 1 < len(content):
                if content[i+1] == '/':
                    in_comment = True
                    i += 1
                elif content[i+1] == '*':
                    in_multiline_comment = True
                    i += 1
            elif char in '"\'`':
                in_string = True
                string_char = char
            elif char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    print(content[start:i+1])
                    print("-" * 40)
                    return
        elif in_string:
            if char == '\\':
                i += 1 # Skip escaped character
            elif char == string_char:
                in_string = False
        elif in_comment:
            if char == '\n':
                in_comment = False
        elif in_multiline_comment:
            if char == '*' and i + 1 < len(content) and content[i+1] == '/':
                in_multiline_comment = False
                i += 1
                
        i += 1

print("--- sendMsg ---")
extract_func('js/main.js', 'sendMsg')
print("--- triggerAIReply ---")
extract_func('js/main.js', 'triggerAIReply')
