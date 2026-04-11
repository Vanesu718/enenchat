import codecs

with codecs.open('js/main.js', 'r', 'utf-8') as f:
    content = f.read()

# 1. Update quickReRoll
old_reroll = """  // 找到第一条AI消息的索引（多气泡的首条）
  const firstAiIdx = rec.length - lastAiMsgs.length;
  const firstAiMsg = rec[firstAiIdx];

  // 初始化 alternatives 数组（存放多个roll版本）
  if (!firstAiMsg.alternatives) {
    firstAiMsg.alternatives = [{
      content: lastAiMsgs.map(m => m.content).join('\n'),
      statusData: lastAiMsgs[lastAiMsgs.length - 1].statusData || null
    }];
    firstAiMsg.currentIndex = 0;
  }"""

new_reroll = """  // 找到第一条AI消息的索引（多气泡的首条）
  const firstAiIdx = rec.length - lastAiMsgs.length;
  const firstAiMsg = rec[firstAiIdx];

  // 将多条消息合并到第一条消息中，并从数组中删除多余的消息
  if (lastAiMsgs.length > 1) {
    firstAiMsg.content = lastAiMsgs.map(m => m.content).join('\n');
    firstAiMsg.statusData = lastAiMsgs[lastAiMsgs.length - 1].statusData || null;
    // 从数组中删除除第一条消息外的其他相关消息
    rec.splice(firstAiIdx + 1, lastAiMsgs.length - 1);
  }

  // 初始化 alternatives 数组（存放多个roll版本）
  if (!firstAiMsg.alternatives) {
    firstAiMsg.alternatives = [{
      content: firstAiMsg.content,
      statusData: firstAiMsg.statusData || null
    }];
    firstAiMsg.currentIndex = 0;
  }

  // 标记当前正在进行重Roll
  firstAiMsg.isRolling = true;"""

content = content.replace(old_reroll, new_reroll)

# 2. Update createMsgElement
old_createMsg = """function createMsgElement(content, side, avatar, quote, idx, type, senderName, statusData) {
  if (idx === undefined) {
    const rec = chatRecords[currentContactId] || [];
    idx = rec.length;
  }

  const div = document.createElement('div');
  const isBlueOfflineCard = isCurrentChatBlueMinimalEnabled() && side === 'left';"""

new_createMsg = """function createMsgElement(content, side, avatar, quote, idx, type, senderName, statusData) {
  if (idx === undefined) {
    const rec = chatRecords[currentContactId] || [];
    idx = rec.length;
  }

  const recCurrent = chatRecords[currentContactId] || [];
  const msgDataNow = recCurrent[idx];

  // 如果正在重Roll且是旧内容，暂时不显示
  if (msgDataNow && msgDataNow.isRolling) {
    const div = document.createElement('div');
    div.style.display = 'none';
    return div;
  }

  const div = document.createElement('div');
  const isBlueOfflineCard = isCurrentChatBlueMinimalEnabled() && side === 'left';"""

content = content.replace(old_createMsg, new_createMsg)

# 3. Update triggerAIReply success (isRolling = false)
old_success = """    if (isThisReRoll) {
      // 重roll模式：追加到alternatives，不新增消息
      const rec = chatRecords[requestContactId] || [];
      const firstAiMsg = rec[pendingReRoll.msgIdx];
      if (firstAiMsg && firstAiMsg.alternatives) {
        const newVersion = {
          content: displayText,
          statusData: parsedStatusData
        };
        firstAiMsg.alternatives.push(newVersion);
        firstAiMsg.currentIndex = firstAiMsg.alternatives.length - 1;
        firstAiMsg.content = displayText;
        firstAiMsg.statusData = parsedStatusData;
        window._pendingReRoll = null;

        await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));"""

new_success = """    if (isThisReRoll) {
      // 重roll模式：追加到alternatives，不新增消息
      const rec = chatRecords[requestContactId] || [];
      const firstAiMsg = rec[pendingReRoll.msgIdx];
      if (firstAiMsg && firstAiMsg.alternatives) {
        const newVersion = {
          content: displayText,
          statusData: parsedStatusData
        };
        firstAiMsg.alternatives.push(newVersion);
        firstAiMsg.currentIndex = firstAiMsg.alternatives.length - 1;
        firstAiMsg.content = displayText;
        firstAiMsg.statusData = parsedStatusData;
        firstAiMsg.isRolling = false;
        window._pendingReRoll = null;

        await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));"""

content = content.replace(old_success, new_success)

# 4. Update triggerAIReply error
old_error = """  } catch (e) { 
      activeAIRequests.delete(requestContactId);
    const isCurrentContact = (requestContactId === currentContactId);
      if (isCurrentContact) {
        document.getElementById('typingStatus').style.display = 'none';
        hideLoading(); 
        addMsgToUI('请求失败：' + e.message, 'left', c.isGroup ? currentSpeaker.avatar : c.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null);
      }
      if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
      chatRecords[requestContactId].push({ side: 'left', content: '请求失败：' + e.message, time: Date.now(), senderId: c.isGroup ? currentSpeaker.id : null });
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      renderContactList();
    }"""

new_error = """  } catch (e) { 
      activeAIRequests.delete(requestContactId);
      const isCurrentContact = (requestContactId === currentContactId);

      const pendingReRoll = window._pendingReRoll;
      const isThisReRollError = isReRoll && pendingReRoll && pendingReRoll.contactId === requestContactId;
      if (isThisReRollError) {
        const rec = chatRecords[requestContactId] || [];
        const firstAiMsg = rec[pendingReRoll.msgIdx];
        if (firstAiMsg) {
           firstAiMsg.isRolling = false;
        }
        window._pendingReRoll = null;
      }

      if (isCurrentContact) {
        document.getElementById('typingStatus').style.display = 'none';
        hideLoading(); 
        addMsgToUI('请求失败：' + e.message, 'left', c.isGroup ? currentSpeaker.avatar : c.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null);
      }
      if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
      chatRecords[requestContactId].push({ side: 'left', content: '请求失败：' + e.message, time: Date.now(), senderId: c.isGroup ? currentSpeaker.id : null });
      await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
      
      if (isThisReRollError && isCurrentContact) renderChat();
      renderContactList();
    }"""

content = content.replace(old_error, new_error)

with codecs.open('js/main.js', 'w', 'utf-8') as f:
    f.write(content)

print("Done")
