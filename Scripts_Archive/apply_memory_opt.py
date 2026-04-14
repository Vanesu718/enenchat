import sys

def modify_main_js():
    with open('js/main.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # The exact block to replace
    search_str = """        if (allowedGroupIds.length > 0) {
            console.log('[记忆互通] 权限已开启，开始检索...');
            const foundMemory = searchCrossChatMemory(currentSpeaker.id, latestRecallMsg.content, allowedGroupIds);
            if (foundMemory) {
              crossChatMemoryPrompt = `\\n（系统旁白：用户刚才提到的话题，你们在共同的群聊里有过对应的交流：\\n${foundMemory}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在群里的发言）\\n`;
              console.log(`[跨频道记忆] 成功注入群组记忆`);
            }
        }
    } else {
        // 是群组聊天
        if (chatSettings.memoryInterconnect) {
            console.log('[记忆互通] 权限已开启，开始检索私聊记忆...');
            const foundPrivateMemory = searchPrivateMemoryForGroup(currentSpeaker.id, latestRecallMsg.content);
            if (foundPrivateMemory) {
              crossChatMemoryPrompt = `\\n（系统旁白：用户刚才提到的话题，你们在私聊里有过对应的交流：\\n${foundPrivateMemory}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在私聊下的约定或信息）\\n`;
              console.log(`[跨频道记忆] 成功注入私聊记忆`);
            }
        }
    }"""
    
    # Try exact match, but it's likely encoding or spacing might mismatch. Let's use regex instead or python string replace on normalized whitespace.
    import re
    
    pattern = re.compile(
        r'if\s*\(\s*allowedGroupIds\.length\s*>\s*0\s*\)\s*\{\s*'
        r'console\.log\(\'\[记忆互通\]\s*权限已开启，开始检索\.\.\.\'\);\s*'
        r'const\s*foundMemory\s*=\s*searchCrossChatMemory\(\s*currentSpeaker\.id\s*,\s*latestRecallMsg\.content\s*,\s*allowedGroupIds\s*\);\s*'
        r'if\s*\(\s*foundMemory\s*\)\s*\{\s*'
        r'crossChatMemoryPrompt\s*=\s*`\\n（系统旁白：用户刚才提到的话题，你们在共同的群聊里有过对应的交流：\\n\$\{foundMemory\}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在群里的发言）\\n`;\s*'
        r'console\.log\(`\[跨频道记忆\]\s*成功注入群组记忆`\);\s*'
        r'\}\s*'
        r'\}\s*'
        r'\}\s*else\s*\{\s*'
        r'//\s*是群组聊天\s*'
        r'if\s*\(\s*chatSettings\.memoryInterconnect\s*\)\s*\{\s*'
        r'console\.log\(\'\[记忆互通\]\s*权限已开启，开始检索私聊记忆\.\.\.\'\);\s*'
        r'const\s*foundPrivateMemory\s*=\s*searchPrivateMemoryForGroup\(\s*currentSpeaker\.id\s*,\s*latestRecallMsg\.content\s*\);\s*'
        r'if\s*\(\s*foundPrivateMemory\s*\)\s*\{\s*'
        r'crossChatMemoryPrompt\s*=\s*`\\n（系统旁白：用户刚才提到的话题，你们在私聊里有过对应的交流：\\n\$\{foundPrivateMemory\}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在私聊下的约定或信息）\\n`;\s*'
        r'console\.log\(`\[跨频道记忆\]\s*成功注入私聊记忆`\);\s*'
        r'\}\s*'
        r'\}\s*'
        r'\}'
    )
    
    replace_str = """        if (allowedGroupIds.length > 0) {
            // 【拦截门1】：检查是否有触发词
            const triggerWords = ['记得', '之前', '说过', '忘了', '刚才', '哪儿', '哪里', '谁'];
            const hasTriggerWord = triggerWords.some(word => latestRecallMsg.content.includes(word));
            
            if (!hasTriggerWord) {
                console.log('[记忆互通] 未触发回忆词，跳过群组检索（0消耗）。');
            } else {
                // 【拦截门2】：检查本地记忆（近期消息、STM、LTM）是否已经包含关键词，避免重复检索
                const localContext = (stmContent + " " + (ltmContent || "") + " " + rawRecs.map(r => r.content).join(" ")).toLowerCase();
                const searchTarget = latestRecallMsg.content.replace(/记得|之前|说过|忘了|刚才|哪儿|哪里|谁|啊|吗|呢/g, '').trim();
                
                const isLocalFound = searchTarget.length >= 2 && localContext.includes(searchTarget);

                if (isLocalFound) {
                    console.log('[记忆互通] 本地记忆已包含该话题，跳过群组检索（0消耗）。');
                } else {
                    console.log('[记忆互通] 触发回忆且本地未找到，开始群组检索...');
                    const foundMemory = searchCrossChatMemory(currentSpeaker.id, latestRecallMsg.content, allowedGroupIds);
                    if (foundMemory) {
                        crossChatMemoryPrompt = `\\n（系统旁白：用户刚才提到的话题，你们在共同的群聊里有过对应的交流：\\n${foundMemory}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在群里的发言）\\n`;
                        console.log(`[跨频道记忆] 成功注入群组记忆`);
                    }
                }
            }
        }
    } else {
        // 是群组聊天
        if (chatSettings.memoryInterconnect) {
            // 【拦截门1】：检查是否有触发词
            const triggerWords = ['记得', '之前', '说过', '忘了', '刚才', '哪儿', '哪里', '谁'];
            const hasTriggerWord = triggerWords.some(word => latestRecallMsg.content.includes(word));
            
            if (!hasTriggerWord) {
                console.log('[记忆互通] 未触发回忆词，跳过私聊检索（0消耗）。');
            } else {
                // 【拦截门2】：检查本地记忆
                const localContext = (stmContent + " " + (ltmContent || "") + " " + rawRecs.map(r => r.content).join(" ")).toLowerCase();
                const searchTarget = latestRecallMsg.content.replace(/记得|之前|说过|忘了|刚才|哪儿|哪里|谁|啊|吗|呢/g, '').trim();
                
                const isLocalFound = searchTarget.length >= 2 && localContext.includes(searchTarget);

                if (isLocalFound) {
                    console.log('[记忆互通] 本地记忆已包含该话题，跳过私聊检索（0消耗）。');
                } else {
                    console.log('[记忆互通] 触发回忆且本地未找到，开始检索私聊记忆...');
                    const foundPrivateMemory = searchPrivateMemoryForGroup(currentSpeaker.id, latestRecallMsg.content);
                    if (foundPrivateMemory) {
                        crossChatMemoryPrompt = `\\n（系统旁白：用户刚才提到的话题，你们在私聊里有过对应的交流：\\n${foundPrivateMemory}\\n请参考该记忆，自然地接着用户的话应答，就像平时说话一样，完全记得你在私聊下的约定或信息）\\n`;
                        console.log(`[跨频道记忆] 成功注入私聊记忆`);
                    }
                }
            }
        }
    }"""
    
    new_content = pattern.sub(replace_str, content)
    
    if content == new_content:
        print("Failed to replace. Pattern did not match.")
    else:
        with open('js/main.js', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully applied optimization to js/main.js")

if __name__ == '__main__':
    modify_main_js()
