const fs = require('fs');

function extractFunc(filepath, funcName) {
    const content = fs.readFileSync(filepath, 'utf-8');
    const regex = new RegExp(`(?:async\\s+)?function\\s+${funcName}\\s*\\(`);
    const match = content.match(regex);
    
    if (!match) {
        console.log(`${funcName} not found`);
        return;
    }
    
    const start = match.index;
    const braceStart = content.indexOf('{', start);
    if (braceStart === -1) return;
    
    let braceCount = 0;
    let inString = false;
    let stringChar = '';
    let inComment = false;
    let inMultilineComment = false;
    
    for (let i = braceStart; i < content.length; i++) {
        const char = content[i];
        
        if (!inString && !inComment && !inMultilineComment) {
            if (char === '/' && i + 1 < content.length) {
                if (content[i+1] === '/') {
                    inComment = true;
                    i++;
                } else if (content[i+1] === '*') {
                    inMultilineComment = true;
                    i++;
                }
            } else if (char === '"' || char === "'" || char === '`') {
                inString = true;
                stringChar = char;
            } else if (char === '{') {
                braceCount++;
            } else if (char === '}') {
                braceCount--;
                if (braceCount === 0) {
                    console.log(content.substring(start, i + 1));
                    console.log('-'.repeat(40));
                    return;
                }
            }
        } else if (inString) {
            if (char === '\\') {
                i++;
            } else if (char === stringChar) {
                inString = false;
            }
        } else if (inComment) {
            if (char === '\n') {
                inComment = false;
            }
        } else if (inMultilineComment) {
            if (char === '*' && i + 1 < content.length && content[i+1] === '/') {
                inMultilineComment = false;
                i++;
            }
        }
    }
}

console.log("--- sendMsg ---");
extractFunc('js/main.js', 'sendMsg');
console.log("--- triggerAIReply ---");
extractFunc('js/main.js', 'triggerAIReply');
