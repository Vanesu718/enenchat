const fs = require('fs');

function modifyMainJs() {
    let content = fs.readFileSync('js/main.js', 'utf8');

    const pattern = /if\s*\(\s*allowedGroupIds\.length\s*>\s*0\s*\)\s*\{\s*console\.log\(\'\[记忆互通\]\s*权限已开启，开始检索\.\.\.\'\);\s*const\s*foundMemory\s*=\s*searchCrossChatMemory\(\s*currentSpeaker\.id\s*,\s*latestRecallMsg\.content\s*,\s*allowedGroupIds\s*\);\s*if\s*\(\s*foundMemory\s*\)\s*\{\s*crossChatMemoryPrompt\s*=\s*`\\n（系统旁白：用户刚才提到的话题，你们在共同的群聊里有过对应的交流：\\n\$\{foundMemory\}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在群里的发言）\\n`;\s*console\.log\(`\[跨频道记忆\]\s*成功注入群组记忆`\);\s*\}\s*\}\s*\}\s*else\s*\{\s*\/\/\s*是群组聊天\s*if\s*\(\s*chatSettings\.memoryInterconnect\s*\)\s*\{\s*console\.log\(\'\[记忆互通\]\s*权限已开启，开始检索私聊记忆\.\.\.\'\);\s*const\s*foundPrivateMemory\s*=\s*searchPrivateMemoryForGroup\(\s*currentSpeaker\.id\s*,\s*latestRecallMsg\.content\s*\);\s*if\s*\(\s*foundPrivateMemory\s*\)\s*\{\s*crossChatMemoryPrompt\s*=\s*`\\n（系统旁白：用户刚才提到的话题，你们在私聊里有过对应的交流：\\n\$\{foundPrivateMemory\}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在私聊下的约定或信息）\\n`;\s*console\.log\(`\[跨频道记忆\]\s*成功注入私聊记忆`\);\s*\}\s*\}\s*\}/g;

    const replaceStr = `if (allowedGroupIds.length > 0) {
            // 【拦截门1】：检查是否有触发词
            const triggerWords = ['记得', '之前', '说过', '忘了', '刚才', '哪儿', '哪里', '谁', '什么'];
            const hasTriggerWord = triggerWords.some(word => latestRecallMsg.content.includes(word));
            
            if (!hasTriggerWord) {
                console.log('[记忆互通] 未触发回忆词，跳过群组检索（0消耗）。');
            } else {
                // 【拦截门2】：检查本地记忆（近期消息、STM、LTM）是否已经包含关键词，避免重复检索
                const localContext = (stmContent + " " + (ltmContent || "") + " " + rawRecs.map(r => r.content).join(" ")).toLowerCase();
                const searchTarget = latestRecallMsg.content.replace(/记得|之前|说过|忘了|刚才|哪儿|哪里|谁|什么|啊|吗|呢/g, '').trim();
                
                const isLocalFound = searchTarget.length >= 2 && localContext.includes(searchTarget);

                if (isLocalFound) {
                    console.log('[记忆互通] 本地记忆已包含该话题，跳过群组检索（0消耗）。');
                } else {
                    console.log('[记忆互通] 触发回忆且本地未找到，开始群组检索...');
                    const foundMemory = searchCrossChatMemory(currentSpeaker.id, latestRecallMsg.content, allowedGroupIds);
                    if (foundMemory) {
                        crossChatMemoryPrompt = \`\\n（系统旁白：用户刚才提到的话题，你们在共同的群聊里有过对应的交流：\\n\${foundMemory}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在群里的发言）\\n\`;
                        console.log(\`[跨频道记忆] 成功注入群组记忆\`);
                    }
                }
            }
        }
    } else {
        // 是群组聊天
        if (chatSettings.memoryInterconnect) {
            // 【拦截门1】：检查是否有触发词
            const triggerWords = ['记得', '之前', '说过', '忘了', '刚才', '哪儿', '哪里', '谁', '什么'];
            const hasTriggerWord = triggerWords.some(word => latestRecallMsg.content.includes(word));
            
            if (!hasTriggerWord) {
                console.log('[记忆互通] 未触发回忆词，跳过私聊检索（0消耗）。');
            } else {
                // 【拦截门2】：检查本地记忆
                const localContext = (stmContent + " " + (ltmContent || "") + " " + rawRecs.map(r => r.content).join(" ")).toLowerCase();
                const searchTarget = latestRecallMsg.content.replace(/记得|之前|说过|忘了|刚才|哪儿|哪里|谁|什么|啊|吗|呢/g, '').trim();
                
                const isLocalFound = searchTarget.length >= 2 && localContext.includes(searchTarget);

                if (isLocalFound) {
                    console.log('[记忆互通] 本地记忆已包含该话题，跳过私聊检索（0消耗）。');
                } else {
                    console.log('[记忆互通] 触发回忆且本地未找到，开始检索私聊记忆...');
                    const foundPrivateMemory = searchPrivateMemoryForGroup(currentSpeaker.id, latestRecallMsg.content);
                    if (foundPrivateMemory) {
                        crossChatMemoryPrompt = \`\\n（系统旁白：用户刚才提到的话题，你们在私聊里有过对应的交流：\\n\${foundPrivateMemory}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在私聊下的约定或信息）\\n\`;
                        console.log(\`[跨频道记忆] 成功注入私聊记忆\`);
                    }
                }
            }
        }
    }`;

    const newContent = content.replace(pattern, replaceStr);

    if (content === newContent) {
        console.log("Failed to replace. Pattern did not match.");
    } else {
        fs.writeFileSync('js/main.js', newContent, 'utf8');
        console.log("Successfully applied optimization to js/main.js");
    }
}

modifyMainJs();