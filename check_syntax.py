import re
import ast

def check_js_syntax():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
            
        scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
        if not scripts:
            print("No scripts found")
            return
            
        js_code = scripts[-1]
        
        # Save to temp file and try to parse it
        with open('temp.js', 'w', encoding='utf-8') as f:
            f.write(js_code)
            
        print("JS code extracted to temp.js")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_js_syntax()