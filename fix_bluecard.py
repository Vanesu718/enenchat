with open('c:/Users/Administrator/Desktop/111/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ==========================================
# 1. Swap 心声 and 心情 in the HTML template
#    AND add 10-char limit for both
# ==========================================
# Original order: 地点, 心情, 心声, 好感度
# New order: 地点, 心声, 心情, 好感度

old_template = (
    '          <div class="bc-status-item"><div class="bc-label">?? \u5730\u70b9</div>'
    '<div class="bc-val">${statusData?.location || \'未知\'}</div></div>\n'
    '          <div class="bc-status-item"><div class="bc-label">?? \u5fc3\u60c5</div>'
    '<div class="bc-val">${statusData?.mood || \'平静\'}</div></div>\n'
    '          <div class="bc-status-item thoughts"><div class="bc-label">?? \u5fc3\u58f0</div>'
    '<div class="bc-val">${statusData?.thoughts || \'没有想法\'}</div></div>\n'
    '          <div class="bc-status-item favor"><div class="bc-label">?? \u597d\u611f\u5ea6</div>'
    '<div class="bc-val">${statusData?.favor || 0}%</div></div>'
)

# Check if old template exists
if old_template in content:
    print("Found exact old template")
else:
    print("Exact match not found, searching for partial...")
    # Find the section
    idx = content.find('bc-status-item')
    print(repr(content[idx-10:idx+500]))
