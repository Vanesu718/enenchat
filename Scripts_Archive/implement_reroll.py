
# -*- coding: utf-8 -*-
"""
实现重roll多版本切换功能
- 重roll不覆盖，而是在聊天气泡下方显示 1/4 2/4 切换按钮
- 用户可以切换保留喜欢的那个版本
- user回复后，锁死选择的版本，清掉其他
"""

import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

print("File loaded, length:", len(content))

# =============================================================
# Step 1: 修改 quickReRoll 函数 - 不再删除AI消息，而是追加到alternatives
# =============================================================

old_reroll = '''async function quickReRoll() {
  toggleChatMenu();
  const rec = chatRecords[currentContactId] || [];
  if (rec.length < 2) { alert('暂无消息可重roll'); return; }
  if (rec[rec.length-1].side !== 'left') { alert('最后一条不是AI回复'); return; }
  
  // 获取最后一条消息的发送者
  const lastSenderId = rec[rec.length-1].senderId;
  
  // 线上模式AI一次回复多条，需循环删除末尾所有属于同一个发送者的AI消息
  while (rec.length > 0 && rec[rec.length - 1].side === 'left' && rec[rec.length - 1].senderId === lastSenderId) {
    rec.pop();
  }
  
  const c = contacts.find(x => x.id === currentContactId);
  // 如果是群聊，我们需要把发言人切回到刚才被删除消息的那个发送者
  if (c && c.isGroup && lastSenderId) {
    const validMembers = c.members.map(id => contacts.find(x => x.id === id)).filter(Boolean);
    const lastIndex = validMembers.findIndex(x => x.id === lastSenderId);
    if (lastIndex >= 0) {
      if (typeof window.groupSpeakerIndices === 'undefined') window.groupSpeakerIndices = {};
      window.groupSpeakerIndices[c.id] = lastIndex;
    }
  }
  
  await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
  renderChat();
  await triggerAIReply(false);
}'''

new_reroll = '''async function quickReRoll() {
  toggleChatMenu();
  const rec = chatRecords[currentContactId] || [];
  if (rec.length < 2) { alert('暂无消息可重roll'); return; }
  if (rec[rec.length-1].side !== 'left') { alert('最后一条不是AI回复'); return; }
  
  // 获取最后一条消息的发送者
  const lastSenderId = rec[rec.length-1].senderId;
  
  // 线上模式下，找到末尾同一个发送者的所有AI消息
  const c = contacts.find(x => x.id === currentContactId);
  
  // 收集末尾连续的同一发送者的AI消息
  const lastAiMsgs = [];
  for (let i = rec.length - 1; i >= 0; i--) {
    if (rec[i].side === 'left' && rec[i].senderId === lastSenderId) {
      lastAiMsgs.unshift(rec[i]);
    } else {
      break;
    }
  }
  
  if (lastAiMsgs.length === 0) { alert('最后一条不是AI回复'); return; }
  
  // 将末尾的AI消息合并为一条（线上模式可能有多条气泡）
  // 找到第一条AI消息的索引（多气泡的首条）
  const firstAiIdx = rec.length - lastAiMsgs.length;
  const firstAiMsg = rec[firstAiIdx];
  
  // 初始化 alternatives 数组（存放多个roll版本）
  if (!firstAiMsg.alternatives) {
    // 把当前这一批气泡合并成第一个版本
    firstAiMsg.alternatives = [{
      content: lastAiMsgs.map(m => m.content).join('\\n'),
      statusData: lastAiMsgs[lastAiMsgs.length - 1].statusData || null,
      msgCount: lastAiMsgs.length,
      msgs: lastAiMsgs.map(m => ({ content: m.content, statusData: m.statusData }))
    }];
    firstAiMsg.currentIndex = 0;
  }
  
  // 记录当前alternatives数量，作为新版本的序号
  const rollNumber = firstAiMsg.alternatives.length + 1;
  
  // 如果是群聊，切回发言人
  if (c && c.isGroup && lastSenderId) {
    const validMembers = c.members.map(id => contacts.find(x => x.id === id)).filter(Boolean);
    const lastIndex = validMembers.findIndex(x => x.id === lastSenderId);
    if (lastIndex >= 0) {
      if (typeof window.groupSpeakerIndices === 'undefined') window.groupSpeakerIndices = {};
      window.groupSpeakerIndices[c.id] = lastIndex;
    }
  }
  
  // 暂存 firstAiMsg 的引用和 rollNumber
  window._pendingReRoll = {
    contactId: currentContactId,
    msgIdx: firstAiIdx,
    rollNumber: rollNumber
  };
  
  await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
  renderChat();
  await triggerAIReply(true); // 传入 isReRoll=true，让AI回复后追加到alternatives而不是push新消息
}'''

if old_reroll in content:
    content = content.replace(old_reroll, new_reroll)
    print("Step 1: quickReRoll replaced successfully")
else:
    print("Step 1: quickReRoll NOT FOUND, trying partial match...")
    if 'async function quickReRoll()' in content:
        print("  -> quickReRoll function exists")
    else:
        print("  -> quickReRoll function NOT FOUND")

# =============================================================
# Step 2: 修改 triggerAIReply 函数签名，加 isReRoll 参数
# =============================================================
old_sig = 'async function triggerAIReply() {\n  if (!currentContactId) { alert'
new_sig = 'async function triggerAIReply(isReRoll = false) {\n  if (!currentContactId) { alert'

if old_sig in content:
    content = content.replace(old_sig, new_sig)
    print("Step 2: triggerAIReply signature updated")
else:
    print("Step 2: triggerAIReply signature NOT found")

# =============================================================
# Step 3: 在triggerAIReply末尾，保存AI消息时，
#         如果是isReRoll模式，追加到alternatives，不push新消息
# =============================================================

# 找到线上模式保存消息的代码块，注入reRoll逻辑
old_save_online = '''    // 线上模式：将回复按换行符拆分为多条独立消息（泡泡）
    if (!isOfflineMode) {
      const lines = displayText.split('\\n').filter(l => l.trim() !== '');
      // 强制限制最多 5 条，防止 AI 话痨
      const limitedLines = lines.slice(0, 5);
      
      limitedLines.forEach(line => {
        if (isCurrentContact) {
          addMsgToUI(line, 'left', currentSpeaker.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null, parsedStatusData);
        }
        if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
        chatRecords[requestContactId].push({ side: 'left', content: line, time: Date.now(), senderId: currentSpeaker.id, statusData: parsedStatusData });
      });
    } else {
      // 线下模式：保持原样，整段发送
      if (isCurrentContact) {
        addMsgToUI(displayText, 'left', currentSpeaker.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null, parsedStatusData);
      }
      if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
      chatRecords[requestContactId].push({ side: 'left', content: displayText, time: Date.now(), senderId: currentSpeaker.id, statusData: parsedStatusData });
    }
    
    await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));'''

new_save_online = '''    // 检查是否是重roll模式
    const pendingReRoll = window._pendingReRoll;
    const isThisReRoll = isReRoll && pendingReRoll && pendingReRoll.contactId === requestContactId;
    
    if (isThisReRoll) {
      // 重roll模式：追加到alternatives，不新增消息
      const rec = chatRecords[requestContactId] || [];
      const firstAiMsg = rec[pendingReRoll.msgIdx];
      if (firstAiMsg && firstAiMsg.alternatives) {
        const newVersion = {
          content: displayText,
          statusData: parsedStatusData,
          msgs: isOfflineMode ? [{ content: displayText, statusData: parsedStatusData }] : displayText.split('\\n').filter(l => l.trim()).slice(0, 5).map(line => ({ content: line, statusData: parsedStatusData }))
        };
        firstAiMsg.alternatives.push(newVersion);
        firstAiMsg.currentIndex = firstAiMsg.alternatives.length - 1;
        firstAiMsg.content = displayText;
        firstAiMsg.statusData = parsedStatusData;
        window._pendingReRoll = null;
        
        await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
        if (isCurrentContact) renderChat();
      }
    } else {
      // 线上模式：将回复按换行符拆分为多条独立消息（泡泡）
      if (!isOfflineMode) {
        const lines = displayText.split('\\n').filter(l => l.trim() !== '');
        // 强制限制最多 5 条，防止 AI 话痨
        const limitedLines = lines.slice(0, 5);
        
        limitedLines.forEach(line => {
          if (isCurrentContact) {
            addMsgToUI(line, 'left', currentSpeaker.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null, parsedStatusData);
          }
          if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
          chatRecords[requestContactId].push({ side: 'left', content: line, time: Date.now(), senderId: currentSpeaker.id, statusData: parsedStatusData });
        });
      } else {
        // 线下模式：保持原样，整段发送
        if (isCurrentContact) {
          addMsgToUI(displayText, 'left', currentSpeaker.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null, parsedStatusData);
        }
        if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
        chatRecords[requestContactId].push({ side: 'left', content: displayText, time: Date.now(), senderId: currentSpeaker.id, statusData: parsedStatusData });
      }
      
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
    }'''

if old_save_online in content:
    content = content.replace(old_save_online, new_save_online)
    print("Step 3: AI reply save logic updated for reRoll")
else:
    print("Step 3: AI reply save logic NOT found - searching for partial match...")
    if "线上模式：将回复按换行符拆分为多条独立消息" in content:
        print("  -> Found the Chinese comment, but block doesn't match exactly")
    else:
        print("  -> Chinese comment NOT found either")

# =============================================================
# Step 4: 在 createMsgElement 中，为有alternatives的消息渲染切换按钮
# =============================================================

# 在 createMsgElement 的函数头部加一个 alternatives 参数 & 渲染逻辑
# 找到函数定义位置，在其末尾（div.onclick之前）加入切换器渲染

old_create_end = '''  div.onclick = () => {
    if (!isBatchDeleteMode) return;
    if (selectedMsgIndices.includes(idx)) {
      selectedMsgIndices = selectedMsgIndices.filter(i => i !== idx);
      div.classList.remove('selected');
    } else {
      selectedMsgIndices.push(idx);
      div.classList.add('selected');
    }
    updateSelectedCount();
  };
  
  return div;
}

function addMsgToUI'''

new_create_end = '''  // 如果有多个roll版本，在气泡下方渲染切换控件
  const rec = chatRecords[currentContactId] || [];
  const msgData = rec[idx];
  if (msgData && msgData.alternatives && msgData.alternatives.length > 1 && side === 'left') {
    const altCount = msgData.alternatives.length;
    const altIdx = (msgData.currentIndex !== undefined ? msgData.currentIndex : altCount - 1) + 1;
    const switcherDiv = document.createElement('div');
    switcherDiv.style.cssText = 'display:flex; align-items:center; justify-content:flex-start; gap:6px; margin-top:4px; margin-left:4px; padding:2px 0;';
    switcherDiv.innerHTML = `
      <button onclick="event.stopPropagation(); switchMsgAlternative(${idx}, 'prev')" style="width:24px; height:24px; border-radius:50%; border:1px solid var(--main-pink); background:rgba(255,255,255,0.8); color:var(--main-pink); font-size:14px; display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0;">‹</button>
      <span style="font-size:11px; color:var(--text-light); background:rgba(255,255,255,0.7); border-radius:10px; padding:1px 8px; border:1px solid rgba(0,0,0,0.08);">${altIdx}/${altCount}</span>
      <button onclick="event.stopPropagation(); switchMsgAlternative(${idx}, 'next')" style="width:24px; height:24px; border-radius:50%; border:1px solid var(--main-pink); background:rgba(255,255,255,0.8); color:var(--main-pink); font-size:14px; display:flex; align-items:center; justify-content:center; cursor:pointer; flex-shrink:0;">›</button>
    `;
    const bubbleWrappers = div.querySelectorAll('[style*="flex-direction:column"]');
    if (bubbleWrappers.length > 0) {
      bubbleWrappers[0].appendChild(switcherDiv);
    } else {
      div.appendChild(switcherDiv);
    }
  }

  div.onclick = () => {
    if (!isBatchDeleteMode) return;
    if (selectedMsgIndices.includes(idx)) {
      selectedMsgIndices = selectedMsgIndices.filter(i => i !== idx);
      div.classList.remove('selected');
    } else {
      selectedMsgIndices.push(idx);
      div.classList.add('selected');
    }
    updateSelectedCount();
  };
  
  return div;
}

function switchMsgAlternative(idx, direction) {
  if (!currentContactId) return;
  const rec = chatRecords[currentContactId];
  if (!rec || !rec[idx]) return;
  
  const msg = rec[idx];
  if (!msg.alternatives || msg.alternatives.length <= 1) return;
  
  const maxIndex = msg.alternatives.length - 1;
  if (direction === 'prev') {
    msg.currentIndex = (msg.currentIndex > 0) ? msg.currentIndex - 1 : maxIndex;
  } else {
    msg.currentIndex = (msg.currentIndex < maxIndex) ? msg.currentIndex + 1 : 0;
  }
  
  const chosen = msg.alternatives[msg.currentIndex];
  msg.content = chosen.content;
  if (chosen.statusData) msg.statusData = chosen.statusData;
  
  saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords)).then(() => {
    renderChat();
  });
}

function addMsgToUI'''

if old_create_end in content:
    content = content.replace(old_create_end, new_create_end)
    print("Step 4: alternatives switcher UI added to createMsgElement")
else:
    print("Step 4: createMsgElement end NOT found")
    if "div.onclick = () => {" in content:
        print("  -> div.onclick found, but surrounding context doesn't match")

# =============================================================
# Step 5: 在 sendMsg 函数中，用户发送时锁死alternatives
# =============================================================

old_send_lock = '''  // 锁死并清空当前聊天列表最后一条AI消息的多余重roll版本
  if (chatRecords[currentContactId] && chatRecords[currentContactId].length > 0) {
    let lastMsg = chatRecords[currentContactId][chatRecords[currentContactId].length - 1];
    if (lastMsg.side === 'left' && lastMsg.alternatives && lastMsg.alternatives.length > 0) {
      lastMsg.content = lastMsg.alternatives[lastMsg.currentIndex || 0].content;
      if (lastMsg.alternatives[lastMsg.currentIndex || 0].statusData) {
        lastMsg.statusData = lastMsg.alternatives[lastMsg.currentIndex || 0].statusData;
      }
      delete lastMsg.alternatives;
      delete lastMsg.currentIndex;
      // 重新渲染UI以隐藏气泡上的切换按钮
      renderChat();
    }
  }'''

new_send_lock = '''  // 锁死并清空当前聊天列表最后一条AI消息的多余重roll版本
  if (chatRecords[currentContactId] && chatRecords[currentContactId].length > 0) {
    for (let i = chatRecords[currentContactId].length - 1; i >= 0; i--) {
      let msg = chatRecords[currentContactId][i];
      if (msg.side === 'left' && msg.alternatives && msg.alternatives.length > 0) {
        const chosen = msg.alternatives[msg.currentIndex || 0];
        msg.content = chosen.content;
        if (chosen.statusData) msg.statusData = chosen.statusData;
        delete msg.alternatives;
        delete msg.currentIndex;
        break; // 只处理最后一条有alternatives的AI消息
      } else if (msg.side === 'right') {
        break; // 遇到用户消息就停止
      }
    }
  }
  window._pendingReRoll = null; // 清空pending'''

if old_send_lock in content:
    content = content.replace(old_send_lock, new_send_lock)
    print("Step 5: sendMsg lock logic updated")
else:
    print("Step 5: sendMsg lock logic NOT found")
    if '锁死并清空当前聊天列表' in content:
        print("  -> Chinese comment found, but block doesn't match")

# =============================================================
# Save the file
# =============================================================
with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n=== All done. File saved. ===")
print("Verifying key strings in output:")
print("  isReRoll:", 'isReRoll = false' in content)
print("  switchMsgAlternative:", 'switchMsgAlternative' in content)
print("  _pendingReRoll:", '_pendingReRoll' in content)
print("  alternatives.length:", 'alternatives.length' in content)
