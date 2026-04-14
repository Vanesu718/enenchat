import re
import sys

def modify_main_js():
    with open('js/main.js', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Update loadChatSettings defaults
    if 'selectedWritingStyle: \'\'' not in content:
        content = re.sub(
            r"(contactMask: '',\s+useWorldBook: true,\s+selectedWorldBooks: \[\])",
            r"\1,\n        selectedWritingStyle: '',\n        compressedWritingStyle: ''",
            content
        )
        
    # 3. Update initChatSettingsPage to populate writing style
    if "const styleSelect = document.getElementById('chatWritingStyleSelect');" not in content:
        init_chat_settings_regex = r"(document\.getElementById\('contactMaskTextarea'\)\.value = [^;]+;)"
        replacement = r"""\1

    // 填充文风下拉菜单
    const styleSelect = document.getElementById('chatWritingStyleSelect');
    if (styleSelect) {
      styleSelect.innerHTML = '<option value="">--不使用文风--</option>';
      writingStyleEntries.forEach(style => {
        const opt = document.createElement('option');
        opt.value = style.id;
        opt.textContent = style.name;
        if (chatSettings.selectedWritingStyle === style.id) {
          opt.selected = true;
        }
        styleSelect.appendChild(opt);
      });
    }"""
        content = re.sub(init_chat_settings_regex, replacement, content, count=1)

    # 4. Implement handleWritingStyleChange function
    if "window.handleWritingStyleChange =" not in content:
        handle_function = """
// 处理文风切换
window.handleWritingStyleChange = async function(styleId) {
  if (!currentContactId) return;
  
  if (styleId === '') {
    chatSettings.selectedWritingStyle = '';
    chatSettings.compressedWritingStyle = '';
    await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
    showToast('已取消文风设置');
    return;
  }
  
  const styleEntry = writingStyleEntries.find(s => s.id === styleId);
  if (!styleEntry) return;
  
  chatSettings.selectedWritingStyle = styleId;
  
  // 显示压缩中提示
  const styleSelect1 = document.getElementById('chatWritingStyleSelect');
  const styleSelect2 = document.getElementById('groupChatWritingStyleSelect');
  const styleSelect = styleSelect1 || styleSelect2;
  
  const originalText = styleSelect ? styleSelect.options[styleSelect.selectedIndex]?.text : '文风';
  if (styleSelect && styleSelect.options[styleSelect.selectedIndex]) {
    styleSelect.options[styleSelect.selectedIndex].text = '压缩处理中...';
  }
  
  try {
    const systemPrompt = "请将以下长篇文风指南压缩成一句约50字的核心行为准则，直接返回结果，不要有任何多余的话语。";
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: styleEntry.content }
        ]
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      const compressed = data.choices[0].message.content.trim();
      chatSettings.compressedWritingStyle = compressed;
      await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
      showToast('文风已应用');
    } else {
      throw new Error('API请求失败');
    }
  } catch (error) {
    console.error('压缩文风失败:', error);
    showToast('压缩文风失败，将使用原始内容的前100字');
    chatSettings.compressedWritingStyle = styleEntry.content.substring(0, 100);
    await saveToStorage(`CHAT_SETTINGS_${currentContactId}`, JSON.stringify(chatSettings));
  } finally {
    if (styleSelect && styleSelect.options[styleSelect.selectedIndex]) {
      styleSelect.options[styleSelect.selectedIndex].text = styleEntry.name;
    }
  }
};
"""
        content = content + "\n" + handle_function
        
    with open('js/main.js', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    modify_main_js()
    print("Modified main.js successfully")
