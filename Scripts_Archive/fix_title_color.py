import re

# Update JS
with open('js/main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# We want to add calculation for --theme-title-color
# function applyThemeColor(main, light, bg) {
#   document.documentElement.style.setProperty('--main-pink', main);
#   ...
#   // Add our logic right after setting --bg-cream

def js_replacement(m):
    return m.group(0) + """
    // Determine title color based on brightness
    let isWhiteOrVeryLight = false;
    try {
      let r, g, b;
      if (main.startsWith('#')) {
        let hex = main.length === 4 ? '#' + main[1]+main[1]+main[2]+main[2]+main[3]+main[3] : main;
        r = parseInt(hex.slice(1,3),16);
        g = parseInt(hex.slice(3,5),16);
        b = parseInt(hex.slice(5,7),16);
      } else if (main.startsWith('rgb')) {
        const parts = main.replace(/rgba?\\(|\\)/g, '').split(',');
        r = parseInt(parts[0]);
        g = parseInt(parts[1]);
        b = parseInt(parts[2]);
      }
      if (r !== undefined && g !== undefined && b !== undefined) {
        const brightness = (r * 299 + g * 587 + b * 114) / 1000;
        if (brightness > 220) {
          isWhiteOrVeryLight = true;
        }
      }
    } catch(e) {}
    
    if (isWhiteOrVeryLight) {
      document.documentElement.style.setProperty('--theme-title-color', '#333333');
    } else {
      document.documentElement.style.setProperty('--theme-title-color', main);
    }
"""

js_content_new = re.sub(
    r"(document\.documentElement\.style\.setProperty\('--bg-cream',\s*bg\);)",
    js_replacement,
    js_content
)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content_new)

# Update CSS
import glob
for filepath in glob.glob('css/*.css'):
    with open(filepath, 'r', encoding='utf-8') as f:
        css = f.read()
    
    # We only want to replace it for text colors, specifically titles, labels.
    # The user points out .form-label, .page-title, .tb-title.
    # To be safe and simple, let's just replace all `color: var(--main-pink);` 
    # with `color: var(--theme-title-color, var(--main-pink));`
    css_new = re.sub(r'color:\s*var\(--main-pink\);', 'color: var(--theme-title-color, var(--main-pink));', css)
    
    if css != css_new:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(css_new)
            print(f"Updated {filepath}")
