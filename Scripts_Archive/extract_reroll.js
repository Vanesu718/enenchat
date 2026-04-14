Line 2941 :       aiRedPacketAction = 'accept';
Line 2942 :       displayText = displayText.replace(/\[ACCEPT_RED_PACKET\]/gi, '').trim();
Line 2943 :     } else if (/\[RETURN_RED_PACKET\]/i.test(displayText)) {
Line 2944 :       aiRedPacketAction = 'return';
Line 2945 :       displayText = displayText.replace(/\[RETURN_RED_PACKET\]/gi, '').trim();
Line 2946 :     } else {
Line 2947 :       const _srpm = displayText.match(/\[SEND_RED_PACKET:\s*([^:\]]+)\s*:\s*([^\]]+)\s*\]/i);
Line 2948 :       if (_srpm) { aiRedPacketAction = { send: { amount: _srpm[1].trim(), msg: _srpm[2].trim() } };
Line 2949 :         displayText = displayText.replace(/\[SEND_RED_PACKET:[^\]]+\]/gi, '').trim();
Line 2950 :       }
Line 2951 :     }  // ===== 红包指令完毕 =====
Line 2952 : 
Line 2953 :   
Line 2954 :     // 检查是否是重roll模式
Line 2955 :     const pendingReRoll = window._pendingReRoll;
Line 2956 :     const isThisReRoll = isReRoll && pendingReRoll && pendingReRoll.contactId === requestContactId;
Line 2957 : 
Line 2958 :     if (isThisReRoll) {
Line 2959 :       // 重roll模式：追加到alternatives，不新增消息
Line 2960 :       const rec = chatRecords[requestContactId] || [];
Line 2961 :       const firstAiMsg = rec[pendingReRoll.msgIdx];
Line 2962 :       if (firstAiMsg && firstAiMsg.alternatives) {
Line 2963 :         const newVersion = {
Line 2964 :           content: displayText,
Line 2965 :           statusData: parsedStatusData
Line 2966 :         };
Line 2967 :         firstAiMsg.alternatives.push(newVersion);
Line 2968 :         firstAiMsg.currentIndex = firstAiMsg.alternatives.length - 1;
Line 2969 :         firstAiMsg.content = displayText;
Line 2970 :         firstAiMsg.statusData = parsedStatusData;
Line 2971 :         delete firstAiMsg.isHidden;
Line 2972 :         window._pendingReRoll = null;
Line 2973 : 
Line 2974 :         await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
Line 2975 :         if (isCurrentContact) renderChat();
Line 2976 :       }
Line 2977 :     } else {
Line 2978 :       // 线上模式：将回复按换行符拆分为多条独立消息（泡泡），逐条延迟显示
Line 2979 :       if (!isOfflineMode) {
Line 2980 :         const lines = displayText.split('\n').filter(l => l.trim() !== '');
Line 2981 :         // 强制限制最多 5 条，防止 AI 话痨
Line 2982 :         const limitedLines = lines.slice(0, 5);
Line 2983 : 
Line 2984 :         // 先将所有消息存入记录
Line 2985 :         if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
Line 2986 :         limitedLines.forEach(line => {
Line 2987 :           chatRecords[requestContactId].push({ side: 'left', content: line, time: Date.now(), senderId: currentSpeaker.id, statusData: parsedStatusData });
Line 2988 :         });
Line 2989 : 
Line 2990 :         // 逐条延迟添加到 UI，每条间隔 600ms，模拟真实聊天节奏
Line 2991 :         if (isCurrentContact) {
Line 2992 :           for (let i = 0; i < limitedLines.length; i++) {
Line 2993 :             if (i > 0) {
Line 2994 :               await new Promise(resolve => setTimeout(resolve, 600));
Line 2995 :             }
Line 2996 :             addMsgToUI(limitedLines[i], 'left', currentSpeaker.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null, parsedStatusData, false);
Line 2997 :           }
Line 2998 :         }
Line 2999 :       } else {
Line 3000 :         // 线下模式：保持原样，整段发送
Line 3001 :         if (isCurrentContact) {
Line 3002 :           addMsgToUI(displayText, 'left', currentSpeaker.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null, parsedStatusData, true);
Line 3003 :         }
Line 3004 :         if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
Line 3005 :         chatRecords[requestContactId].push({ side: 'left', content: displayText, time: Date.now(), senderId: currentSpeaker.id, statusData: parsedStatusData, isOfflineMsg: true });
Line 3006 :       }
Line 3007 : 
Line 3008 :       await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
Line 3009 :     }
Line 3010 :     
Line 3011 :   // 恢复群聊有序发言功能
Line 3012 :   if (c.isGroup && isCurrentContact) {
Line 3013 :     const validMembers = c.members.map(id => contacts.find(x => x.id === id)).filter(Boolean);
Line 3014 :     if (validMembers.length > 0) {
Line 3015 :       if (typeof window.groupSpeakerIndices === 'undefined') window.groupSpeakerIndices = {};
Line 3016 :       let currentIndex = window.groupSpeakerIndices[c.id] || 0;
Line 3017 :       window.groupSpeakerIndices[c.id] = (currentIndex + 1) % validMembers.length;
Line 3018 :       
Line 3019 :       // 如果还没轮完一圈，继续触发下一个人的回复
Line 3020 :       if (window.groupSpeakerIndices[c.id] !== 0) {
Line 3021 :           setTimeout(() => {
Line 3022 :             if (activeAIRequests.has(currentContactId)) return;
Line 3023 :             triggerAIReply();
Line 3024 :           }, 1000);
Line 3025 :       }
Line 3026 :     }
Line 3027 :   }
Line 3028 : 
Line 3029 :   // 如果当前在别的聊天窗口，重新渲染聊天记录（因为可能刚好切到了别的窗口，这时候不应该显示刚才那个人的消息）
Line 3030 :   if (!isCurrentContact && document.getElementById('chat-win').classList.contains('show')) {
Line 3031 :       renderChat();
Line 3032 :   }
Line 3033 :   
Line 3034 :   renderContactList();
Line 3035 :     
Line 3036 :     // 检查是否需要触发短期记忆总结 (传入正确的联系人ID)
Line 3037 :     checkAndTriggerStmForContact(requestContactId)
Line 3038 :   // ===== AI红包行为处理 =====
Line 3039 :   if (aiRedPacketAction && requestContactId) {
Line 3040 :     const _rpCid = requestContactId;
Line 3041 :     const _rpRecs = chatRecords[_rpCid] || [];
Line 3042 :     // 找到最近一条用户发出的红包
Line 3043 :     const _rpMsg = [..._rpRecs].reverse().find(m => m.side==='right' && m.type==='red_packet');
Line 3044 :       if (aiRedPacketAction==='accept' && _rpMsg) {
Line 3045 :         _rpMsg.rpStatus = 'accepted';
Line 3046 :         const c = contacts.find(x => x.id === _rpCid) || {name:'对方'};
Line 3047 :         const uName = chatSettings.chatNickname || window.storageSync?.getItem('USER_NICKNAME') || '你';
Line 3048 :         const notif = { side:'notif', type:'rp_notif', content: '<div style="text-align:center;font-size:12px;color:#999;margin:10px 0;"><img src="ICON/红包.png" style="width:12px;height:14px;margin-right:2px;vertical-align:-2px;filter:drop-shadow(0 0 1px rgba(0,0,0,0.2));">' + c.name + '领取了' + uName + '的红包</div>', time:Date.now() };
Line 3049 :         chatRecords[_rpCid].push(notif);
Line 3050 :         await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
Line 3051 :       if (isCurrentContact) renderChat();
Line 3052 :     } else if (aiRedPacketAction==='return' && _rpMsg) {
Line 3053 :       _rpMsg.rpStatus = 'returned';
Line 3054 :       const notif = { side:'notif', type:'rp_notif', content:'<div style="text-align:center;font-size:12px;color:#999;margin:10px 0;"><img src="ICON/红包.png" style="width:12px;height:14px;margin-right:2px;vertical-align:-2px;filter:drop-shadow(0 0 1px rgba(0,0,0,0.2));">对方已退回红包</div>', time:Date.now() };
Line 3055 :       chatRecords[_rpCid].push(notif);
Line 3056 :       await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
Line 3057 :       if (isCurrentContact) renderChat();
Line 3058 :     } else if (aiRedPacketAction && aiRedPacketAction.send) {
Line 3059 :       const _s = aiRedPacketAction.send;
Line 3060 :       const c = contacts.find(x => x.id === _rpCid) || {avatar:''};
Line 3061 :       const _content = JSON.stringify({ amount: _s.amount, msg: _s.msg, cover: c.avatar });
Line 3062 :       const _aiRp = { side:'left', type:'red_packet', content: _content, time:Date.now() };
Line 3063 :       chatRecords[_rpCid].push(_aiRp);
Line 3064 :       await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
Line 3065 :       if (isCurrentContact) renderChat();
Line 3066 :     }
Line 3067 :   }
Line 3068 :   // ===== AI红包行为处理完毕 =====;
Line 3069 :     
Line 3070 :   } catch (e) { 
Line 3071 :       activeAIRequests.delete(requestContactId);
Line 3072 :       const pendingReRoll = window._pendingReRoll;
Line 3073 :       if (isReRoll && pendingReRoll && pendingReRoll.contactId === requestContactId) {
Line 3074 :         const rec = chatRecords[requestContactId] || [];
Line 3075 :         const firstAiMsg = rec[pendingReRoll.msgIdx];
Line 3076 :         if (firstAiMsg) delete firstAiMsg.isHidden;
Line 3077 :         window._pendingReRoll = null;
Line 3078 :       }
Line 3079 :       const isCurrentContact = (requestContactId === currentContactId);
Line 3080 :       if (isCurrentContact) {
Line 3081 :         document.getElementById('typingStatus').style.display = 'none';
Line 3082 :         hideLoading(); 
Line 3083 :         addMsgToUI('请求失败：' + e.message, 'left', c.isGroup ? currentSpeaker.avatar : c.avatar, null, undefined, undefined, false, c.isGroup ? currentSpeaker.name : null);
Line 3084 :       }
Line 3085 :       if (!chatRecords[requestContactId]) chatRecords[requestContactId] = [];
Line 3086 :       chatRecords[requestContactId].push({ side: 'left', content: '请求失败：' + e.message, time: Date.now(), senderId: c.isGroup ? currentSpeaker.id : null });
Line 3087 :       await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
Line 3088 :       if (isCurrentContact) renderChat();
Line 3089 :       renderContactList();
Line 3090 :     }
Line 3091 : }
Line 3092 : 
Line 3093 : // 专门为特定联系人触发STM的函数
Line 3094 : async function checkAndTriggerStmForContact(contactId) {
Line 3095 :   if (!contactId) return;
Line 3096 :   const memSettingsStr = await window.storage.getItem('MEMORY_SETTINGS');
Line 3097 :   const memSettings = memSettingsStr ? (typeof memSettingsStr === 'string' ? JSON.parse(memSettingsStr) : memSettingsStr) : {};
Line 3098 :   if (!memSettings.stmAutoEnabled) return;
Line 3099 : 
Line 3100 :   const stm = await getStmData(contactId);
