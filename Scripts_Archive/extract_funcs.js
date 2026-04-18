const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf8');

function extractFunction(name) {
    let idx = content.indexOf(`async function ${name}(`);
    if (idx === -1) {
        idx = content.indexOf(`function ${name}(`);
        if (idx === -1) {
            idx = content.indexOf(`${name}: function`);
            if (idx === -1) {
                return `${name} not found`;
            }
        }
    }
    
    let startBrace = content.indexOf('{', idx);
    let braceCount = 1;
    let i = startBrace + 1;
    while (braceCount > 0 && i < content.length) {
        if (content[i] === '{') braceCount++;
        else if (content[i] === '}') braceCount--;
        i++;
    }
    return content.substring(idx, i);
}

fs.writeFileSync('extracted_funcs.txt', 
    extractFunction('triggerAIReply') + '\n\n' +
    extractFunction('handleReRoll') + '\n\n' +
    extractFunction('processOnlineResponse') + '\n\n' +
    extractFunction('parseMessage')
);
