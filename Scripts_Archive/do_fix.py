import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix the syntax error
content = content.replace("renderContactLis\n    // trigger AI after sending red packet\n    setTimeout(function(){ if(typeof triggerAIReply==='function') triggerAIReply(); }, 300);t();", "renderContactList();\n    // trigger AI after sending red packet\n    setTimeout(function(){ if(typeof triggerAIReply==='function') triggerAIReply(); }, 300);")

# 2. Update triggerAIReply prompt
old_prompt = """    // Inject AI Emoji prompt addon if enabled (异步版本)
    if (typeof getAiEmojiPromptAddon === 'function') {
        systemPrompt += await getAiEmojiPromptAddon();
    }
     // ===== RP prompt inject =====
    { var _rpL=(rawRecs||[]).slice().reverse().find(function(m){return m.side==='right' && m.type==='red_packet';});if(_rpL&&!_rpL.rpStatus){var _ra=_rpL.rpAmount||'';var _rm=_rpL.rpMsg||'Best wishes';systemPrompt+='\\n\\n[HongBao] User sent you a red packet. Amount:'+_ra+', msg:'+_rm+'. Append ONE tag at end of reply: [ACCEPT_RED_PACKET] or [RETURN_RED_PACKET] or [SEND_RED_PACKET:amount:blessing]';}}
    // ===== end RP inject ====="""

new_prompt = """    // Inject AI Emoji prompt addon if enabled (异步版本)
    if (typeof getAiEmojiPromptAddon === 'function') {
        systemPrompt += await getAiEmojiPromptAddon();
    }
     // ===== RP prompt inject =====
    systemPrompt += '\\n\\n【红包机制】你可以在回复末尾添加 [SEND_RED_PACKET:金额:留言] 主动给用户发送红包。';
    {
      var _rpL=(rawRecs||[]).slice().reverse().find(function(m){return m.side==='right' && m.type==='red_packet';});
      if(_rpL&&!_rpL.rpStatus){
        var _rpData = {};
        try { _rpData = JSON.parse(_rpL.content); } catch(e) { _rpData = {msg: _rpL.content}; }
        var _ra=_rpData.amount||'';var _rm=_rpData.msg||'Best wishes';
        systemPrompt+='\\n[HongBao] User sent you a red packet. Amount:'+_ra+', msg:'+_rm+'. Append ONE tag at end of reply: [ACCEPT_RED_PACKET] or [RETURN_RED_PACKET]';
      }
    }
    // ===== end RP inject ====="""
content = content.replace(old_prompt, new_prompt)

# 3. Update AI action handling
old_action = """  // ===== AI红包行为处理 =====
  if (aiRedPacketAction && requestContactId) {
    const _rpCid = requestContactId;
    const _rpRecs = chatRecords[_rpCid] || [];
    // 找到最近一条用户发出的红包
    const _rpMsg = [..._rpRecs].reverse().find(m => m.side==='right' && m.type==='red_packet');
    if (aiRedPacketAction==='accept' && _rpMsg) {
      _rpMsg.rpStatus = 'accepted';
      const notif = { side:'notif', type:'rp_notif', content:'对方已接收红包', time:Date.now() };
      chatRecords[_rpCid].push(notif);
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      if (isCurrentContact) renderChat();
    } else if (aiRedPacketAction==='return' && _rpMsg) {
      _rpMsg.rpStatus = 'returned';
      const notif = { side:'notif', type:'rp_notif', content:'对方已退回红包', time:Date.now() };
      chatRecords[_rpCid].push(notif);
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      if (isCurrentContact) renderChat();
    } else if (aiRedPacketAction && aiRedPacketAction.send) {
      const _s = aiRedPacketAction.send;
      const _aiRp = { side:'left', type:'red_packet', rpAmount:_s.amount, rpMsg:_s.msg, rpCover:'', time:Date.now() };
      chatRecords[_rpCid].push(_aiRp);
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      if (isCurrentContact) renderChat();
    }
  }
  // ===== AI红包行为处理完毕 =====;"""

new_action = """  // ===== AI红包行为处理 =====
  if (aiRedPacketAction && requestContactId) {
    const _rpCid = requestContactId;
    const _rpRecs = chatRecords[_rpCid] || [];
    // 找到最近一条用户发出的红包
    const _rpMsg = [..._rpRecs].reverse().find(m => m.side==='right' && m.type==='red_packet');
    
    const aiName = currentSpeaker ? currentSpeaker.name : ((contacts.find(c => c.id === _rpCid) || {}).name || '对方');
    let chatSettingsForContact = {};
    const savedSettings = await getFromStorage(`CHAT_SETTINGS_${_rpCid}`);
    if (savedSettings) {
      chatSettingsForContact = typeof savedSettings === 'string' ? JSON.parse(savedSettings) : savedSettings;
    }
    const userName = chatSettingsForContact.chatNickname || await getFromStorage('USER_NICKNAME') || '我';

    if (aiRedPacketAction==='accept' && _rpMsg) {
      _rpMsg.rpStatus = 'accepted';
      const notif = { side:'notif', type:'rp_notif', content:`${aiName}领取了${userName}的红包。`, time:Date.now() };
      chatRecords[_rpCid].push(notif);
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      if (isCurrentContact) renderChat();
    } else if (aiRedPacketAction==='return' && _rpMsg) {
      _rpMsg.rpStatus = 'returned';
      const notif = { side:'notif', type:'rp_notif', content:`${aiName}退回了${userName}的红包。`, time:Date.now() };
      chatRecords[_rpCid].push(notif);
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      if (isCurrentContact) renderChat();
    } else if (aiRedPacketAction && aiRedPacketAction.send) {
      const _s = aiRedPacketAction.send;
      const aiAvatar = currentSpeaker ? currentSpeaker.avatar : ((contacts.find(c => c.id === _rpCid) || {}).avatar || '');
      const _aiRp = { side:'left', type:'red_packet', content: JSON.stringify({ amount: _s.amount, msg: _s.msg, cover: aiAvatar }), rpStatus: null, time:Date.now() };
      chatRecords[_rpCid].push(_aiRp);
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      if (isCurrentContact) renderChat();
    }
  }
  // ===== AI红包行为处理完毕 =====;"""
content = content.replace(old_action, new_action)


# 4. Update createMsgElement to show status correctly
old_create = """        if (isRedPacket) {
          const coverUrl = data.cover || '';
          const rpMsg = data.msg || '恭喜发财，大吉大利';
          const rpAmt = data.amount || '';
          const coverBg = coverUrl ? ('url('+coverUrl+') center/cover no-repeat') : 'linear-gradient(160deg,#e8334a,#c62135)';
          box.style.cssText = 'width:140px;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 8px rgba(0,0,0,0.18);cursor:pointer;user-select:none;';
          box.innerHTML = '<div class="rp-bubble-top" style="position:relative;width:100%;height:150px;background:'+coverBg+';display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:20px;"><div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.1);border-radius:12px 12px 0 0;"></div><div style="position:relative;z-index:1;text-align:center;padding:0 10px;"><div style="color:#fff;font-size:15px;font-weight:bold;text-shadow:0 1px 4px rgba(0,0,0,0.5);">'+rpMsg+'</div></div></div><div style="background:#c62135;padding:12px 0;display:flex;align-items:center;justify-content:center;"><div class="rp-open-coin" style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#f5deb3,#d4a56a);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:bold;color:#8b4513;box-shadow:0 2px 6px rgba(0,0,0,0.2);">開</div></div>';
          if (side === 'right') { box.style.cursor = 'default'; } else { box.onclick = (e) => { e.stopPropagation(); openRedPacket(box, rpAmt, rpMsg, coverUrl); }; }
        } else {"""

new_create = """        if (isRedPacket) {
          const coverUrl = data.cover || '';
          const rpMsg = data.msg || '恭喜发财，大吉大利';
          const rpAmt = data.amount || '';
          const coverBg = coverUrl ? ('url('+coverUrl+') center/cover no-repeat') : 'linear-gradient(160deg,#e8334a,#c62135)';
          
          let _msgData = {};
          if (idx !== undefined && chatRecords[currentContactId]) {
            _msgData = chatRecords[currentContactId][idx] || {};
          }
          let isAccepted = _msgData.rpStatus === 'accepted';
          
          box.style.cssText = 'width:140px;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 2px 8px rgba(0,0,0,0.18);cursor:pointer;user-select:none;';
          
          if (isAccepted) {
            box.innerHTML = '<div class="rp-bubble-top" style="position:relative;width:100%;height:150px;background:'+coverBg+';display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:20px;filter:grayscale(0.5);"><div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.1);border-radius:12px 12px 0 0;"></div><div style="position:relative;z-index:1;text-align:center;padding:0 10px;"><div style="color:#fff;font-size:15px;font-weight:bold;text-shadow:0 1px 4px rgba(0,0,0,0.5);">'+rpMsg+'</div></div></div><div style="background:#c62135;padding:12px 0;display:flex;align-items:center;justify-content:center;"><div class="rp-open-coin" style="width:40px;height:40px;border-radius:50%;background:#aaa;display:flex;align-items:center;justify-content:center;font-size:13px;color:#fff;box-shadow:0 2px 6px rgba(0,0,0,0.2);">已收</div></div>';
            box.style.cursor = 'default';
          } else {
            box.innerHTML = '<div class="rp-bubble-top" style="position:relative;width:100%;height:150px;background:'+coverBg+';display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:20px;"><div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.1);border-radius:12px 12px 0 0;"></div><div style="position:relative;z-index:1;text-align:center;padding:0 10px;"><div style="color:#fff;font-size:15px;font-weight:bold;text-shadow:0 1px 4px rgba(0,0,0,0.5);">'+rpMsg+'</div></div></div><div style="background:#c62135;padding:12px 0;display:flex;align-items:center;justify-content:center;"><div class="rp-open-coin" style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#f5deb3,#d4a56a);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:bold;color:#8b4513;box-shadow:0 2px 6px rgba(0,0,0,0.2);">開</div></div>';
            if (side === 'right') { box.style.cursor = 'default'; } else { box.onclick = (e) => { e.stopPropagation(); openRedPacket(box, rpAmt, rpMsg, coverUrl, idx, senderName); }; }
          }
        } else {"""
content = content.replace(old_create, new_create)


# 5. Update openRedPacket function
old_open = """function openRedPacket(elem, amount, msg, cover) {
    if (elem._rpOpened) return;
    var ex = document.getElementById('rpChoiceModal');
    if (ex) ex.remove();
    var cs = cover ? ('url('+cover+') center/cover no-repeat') : 'linear-gradient(160deg,#e8334a,#c62135)';
    var sm = msg || '恭喜发财，大吉大利';
    var sa = amount || '0.00';
    var modal = document.createElement('div');
    modal.id = 'rpChoiceModal';
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;';
    modal.innerHTML = '<div style="width:260px;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.35);display:flex;flex-direction:column;"><div style="position:relative;width:100%;height:320px;background:'+cs+';display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:40px;"><div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.1);"></div><div style="position:relative;z-index:1;text-align:center;padding:0 16px;"><div style="color:#fff;font-size:18px;font-weight:bold;text-shadow:0 1px 4px rgba(0,0,0,0.6);">'+sm+'</div><div style="color:rgba(255,255,255,0.9);font-size:14px;margin-top:6px;">&yen;'+sa+'</div></div></div><div style="background:#c62135;padding:16px 20px;display:flex;gap:12px;justify-content:center;"><button id="rpChoiceAccept" style="flex:1;padding:10px 0;border:none;border-radius:24px;background:linear-gradient(135deg,#f5deb3,#d4a56a);color:#6b3a1f;font-size:16px;font-weight:bold;cursor:pointer;">收下</button><button id="rpChoiceReturn" style="flex:1;padding:10px 0;border:none;border-radius:24px;background:rgba(255,255,255,0.2);color:#fff;font-size:16px;cursor:pointer;">退回</button></div></div>';
    document.body.appendChild(modal);
    modal.addEventListener('click', function(e){ if(e.target===modal) modal.remove(); });
    document.getElementById('rpChoiceAccept').onclick = function() {
        modal.remove(); elem._rpOpened = true;
        var coin = elem.querySelector('.rp-open-coin');
        if (coin) { coin.textContent='已收'; coin.style.background='#aaa'; coin.style.color='#fff'; coin.style.fontSize='13px'; }
        var t2 = elem.querySelector('.rp-bubble-top');
        if (t2) t2.style.filter='grayscale(0.5)';
        if (typeof showToast==='function') showToast('红包已收下 \u00a5'+amount);
    };
    document.getElementById('rpChoiceReturn').onclick = function() {
        modal.remove();
        if (typeof showToast==='function') showToast('红包已退回');
    };
}"""

new_open = """function openRedPacket(elem, amount, msg, cover, msgIdx, senderName) {
    if (elem._rpOpened) return;
    var ex = document.getElementById('rpChoiceModal');
    if (ex) ex.remove();
    var cs = cover ? ('url('+cover+') center/cover no-repeat') : 'linear-gradient(160deg,#e8334a,#c62135)';
    var sm = msg || '恭喜发财，大吉大利';
    var sa = amount || '0.00';
    var modal = document.createElement('div');
    modal.id = 'rpChoiceModal';
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9999;display:flex;align-items:center;justify-content:center;';
    modal.innerHTML = '<div style="width:260px;border-radius:16px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.35);display:flex;flex-direction:column;"><div style="position:relative;width:100%;height:320px;background:'+cs+';display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:40px;"><div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.1);"></div><div style="position:relative;z-index:1;text-align:center;padding:0 16px;"><div style="color:#fff;font-size:18px;font-weight:bold;text-shadow:0 1px 4px rgba(0,0,0,0.6);">'+sm+'</div><div style="color:rgba(255,255,255,0.9);font-size:14px;margin-top:6px;">&yen;'+sa+'</div></div></div><div style="background:#c62135;padding:16px 20px;display:flex;gap:12px;justify-content:center;"><button id="rpChoiceAccept" style="flex:1;padding:10px 0;border:none;border-radius:24px;background:linear-gradient(135deg,#f5deb3,#d4a56a);color:#6b3a1f;font-size:16px;font-weight:bold;cursor:pointer;">收下</button><button id="rpChoiceReturn" style="flex:1;padding:10px 0;border:none;border-radius:24px;background:rgba(255,255,255,0.2);color:#fff;font-size:16px;cursor:pointer;">退回</button></div></div>';
    document.body.appendChild(modal);
    modal.addEventListener('click', function(e){ if(e.target===modal) modal.remove(); });
    document.getElementById('rpChoiceAccept').onclick = async function() {
        modal.remove(); elem._rpOpened = true;
        var coin = elem.querySelector('.rp-open-coin');
        if (coin) { coin.textContent='已收'; coin.style.background='#aaa'; coin.style.color='#fff'; coin.style.fontSize='13px'; }
        var t2 = elem.querySelector('.rp-bubble-top');
        if (t2) t2.style.filter='grayscale(0.5)';
        elem.style.cursor = 'default';
        elem.onclick = null;
        if (typeof showToast==='function') showToast('红包已收下 \u00a5'+amount);

        // 持久化状态并推送系统提示
        if (msgIdx !== undefined && currentContactId && chatRecords[currentContactId]) {
          const rec = chatRecords[currentContactId][msgIdx];
          if (rec) {
            rec.rpStatus = 'accepted';
            let userName = '我';
            try {
               let chatSettingsForContact = {};
               const savedSettings = await getFromStorage(`CHAT_SETTINGS_${currentContactId}`);
               if (savedSettings) {
                 chatSettingsForContact = typeof savedSettings === 'string' ? JSON.parse(savedSettings) : savedSettings;
               }
               userName = chatSettingsForContact.chatNickname || await getFromStorage('USER_NICKNAME') || '我';
            } catch(e) {}
            const aiName = senderName || (contacts.find(c => c.id === currentContactId) || {}).name || '对方';
            const notif = { side:'notif', type:'rp_notif', content:`${userName}领取了${aiName}的红包。`, time:Date.now() };
            chatRecords[currentContactId].push(notif);
            await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
            if (typeof renderChat === 'function') renderChat();
          }
        }
    };
    document.getElementById('rpChoiceReturn').onclick = async function() {
        modal.remove();
        if (typeof showToast==='function') showToast('红包已退回');
        
        if (msgIdx !== undefined && currentContactId && chatRecords[currentContactId]) {
          const rec = chatRecords[currentContactId][msgIdx];
          if (rec) {
            rec.rpStatus = 'returned';
            let userName = '我';
            try {
               let chatSettingsForContact = {};
               const savedSettings = await getFromStorage(`CHAT_SETTINGS_${currentContactId}`);
               if (savedSettings) {
                 chatSettingsForContact = typeof savedSettings === 'string' ? JSON.parse(savedSettings) : savedSettings;
               }
               userName = chatSettingsForContact.chatNickname || await getFromStorage('USER_NICKNAME') || '我';
            } catch(e) {}
            const aiName = senderName || (contacts.find(c => c.id === currentContactId) || {}).name || '对方';
            const notif = { side:'notif', type:'rp_notif', content:`${userName}退回了${aiName}的红包。`, time:Date.now() };
            chatRecords[currentContactId].push(notif);
            await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
            if (typeof renderChat === 'function') renderChat();
          }
        }
    };
}"""
content = content.replace(old_open, new_open)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)
