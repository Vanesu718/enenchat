import os

file_path = os.path.join(os.path.dirname(__file__), 'js', 'main.js')

with open(file_path, 'r', encoding='utf-8') as f:
    code = f.read()

save_search = """  // 检查是否包含"两人初始"或"刚认识"等词以重置好感度（现绑定到 contactMemo）
  if (chatSettings.contactMemo && (chatSettings.contactMemo.includes('两人初始') || chatSettings.contactMemo.includes('刚认识') || chatSettings.contactMemo.includes('初次见面') || chatSettings.contactMemo.includes('第一天'))) {
    const savedStatus = await getFromStorage(`STATUS_${currentContactId}`);
    if (savedStatus) {
      const status = typeof savedStatus === 'string' ? JSON.parse(savedStatus) : savedStatus;
      status.favor = 0;
      await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
      // 如果当前状态卡片打开，更新UI
      const favorBar = document.getElementById('status-favor');
      const favorText = document.getElementById('status-favor-text');
      if (favorBar) favorBar.style.width = '0%';
      if (favorText) favorText.textContent = '0%';
    } else {
      // 即使之前没有状态，也创建一个初始状态并设好感度为0
      const status = { location: '未知', mood: '平静', thoughts: '暂无数据', favor: 0 };
      await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
    }
  }"""

save_replace = """  // 检查是否包含"恋人"或"已婚"等词以初始化好感度
  let initFavor = 0;
  if (chatSettings.contactMemo && (chatSettings.contactMemo.includes('恋人') || chatSettings.contactMemo.includes('已婚') || chatSettings.contactMemo.includes('交往'))) {
    initFavor = 60;
  }
  
  const savedStatus = await getFromStorage(`STATUS_${currentContactId}`);
  if (savedStatus) {
    const status = typeof savedStatus === 'string' ? JSON.parse(savedStatus) : savedStatus;
    // 如果设定为恋人等，且好感度之前为0，则提升到60
    if (status.favor === 0 && initFavor === 60) {
      status.favor = 60;
      await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
      const favorBar = document.getElementById('status-favor');
      const favorText = document.getElementById('status-favor-text');
      if (favorBar) favorBar.style.width = '60%';
      if (favorText) favorText.textContent = '60%';
    } else if (status.favor !== 0 && initFavor === 0 && (chatSettings.contactMemo.includes('两人初始') || chatSettings.contactMemo.includes('刚认识') || chatSettings.contactMemo.includes('初次见面') || chatSettings.contactMemo.includes('第一天'))) {
      // 如果明确指定刚认识，重置为0
      status.favor = 0;
      await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
      const favorBar = document.getElementById('status-favor');
      const favorText = document.getElementById('status-favor-text');
      if (favorBar) favorBar.style.width = '0%';
      if (favorText) favorText.textContent = '0%';
    }
  } else {
    // 即使之前没有状态，也创建一个初始状态并设好感度为 initFavor
    const status = { location: '未知', mood: '平静', thoughts: '暂无数据', favor: initFavor };
    await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
  }"""

code = code.replace(save_search, save_replace)

clear_search = """  // 3. 重置状态(好感度等)
  const status = { location: '未知', mood: '平静', thoughts: '暂无数据', favor: 0 };
  await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
  
  // 如果状态卡片打开，更新UI
  const favorBar = document.getElementById('status-favor');
  const favorText = document.getElementById('status-favor-text');
  if (favorBar) favorBar.style.width = '0%';
  if (favorText) favorText.textContent = '0%';"""

clear_replace = """  // 3. 重置状态(好感度等)
  let initFavor = 0;
  if (typeof chatSettings !== 'undefined' && chatSettings && chatSettings.contactMemo && (chatSettings.contactMemo.includes('恋人') || chatSettings.contactMemo.includes('已婚') || chatSettings.contactMemo.includes('交往'))) {
    initFavor = 60;
  }
  const status = { location: '未知', mood: '平静', thoughts: '暂无数据', favor: initFavor };
  await saveToStorage(`STATUS_${currentContactId}`, JSON.stringify(status));
  
  // 如果状态卡片打开，更新UI
  const favorBar = document.getElementById('status-favor');
  const favorText = document.getElementById('status-favor-text');
  if (favorBar) favorBar.style.width = initFavor + '%';
  if (favorText) favorText.textContent = initFavor + '%';"""

code = code.replace(clear_search, clear_replace)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(code)

print('Fixed js/main.js')
