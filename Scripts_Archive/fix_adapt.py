import os
import re

css_file = 'css/index-main.css'
js_file = 'js/main.js'

with open(css_file, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Add dvh fallbacks and visualViewport support
# Replace min-height: 100vh with dvh fallback
css_content = re.sub(r'min-height:\s*100vh;', 'min-height: 100vh;\n  min-height: 100dvh;', css_content)
css_content = re.sub(r'height:\s*100vh\s*!important;', 'height: 100vh !important;\n  height: 100dvh !important;', css_content)

# Add modal mobile fix
modal_fix = """

/* Mobile adaptation for Modal and Chat */
@media (max-width: 768px) {
  .modal-content {
    position: fixed !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    max-height: 85vh !important;
    max-height: 85dvh !important;
    width: 90% !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
  }
  
  /* Fallback for Yujian/Via bounds */
  body, html {
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
  }
  
  .chat-container {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}
"""
if "/* Mobile adaptation for Modal and Chat */" not in css_content:
    css_content += modal_fix

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css_content)

with open(js_file, 'r', encoding='utf-8') as f:
    js_content = f.read()

# visualViewport JS fix for keyboard
js_fix = """
// HarmonyOS & Mobile Keyboard Fix
(function() {
    if (window.visualViewport) {
        window.visualViewport.addEventListener('resize', function() {
            document.body.style.height = window.visualViewport.height + 'px';
            window.scrollTo(0, 0);
        });
    }
    
    // Focus scrollIntoView for inputs
    document.addEventListener('focusin', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            setTimeout(function() {
                e.target.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }, 300);
        }
    });
})();
"""

if "HarmonyOS & Mobile Keyboard Fix" not in js_content:
    js_content += "\n" + js_fix

with open(js_file, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Fix applied.")
