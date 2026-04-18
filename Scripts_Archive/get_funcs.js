const fs = require('fs');

const content = fs.readFileSync('js/main.js', 'utf8');
const lines = content.split('\n');

let start = -1;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('function createMsgElement(')) {
        start = i;
        break;
    }
}

if (start !== -1) {
    let braces = 0;
    let started = false;
    let end = start;
    for (let i = start; i < lines.length; i++) {
        let line = lines[i];
        if (line.includes('{')) {
            braces += (line.match(/\{/g) || []).length;
            started = true;
        }
        if (line.includes('}')) {
            braces -= (line.match(/\}/g) || []).length;
        }
        if (started && braces === 0) {
            end = i;
            break;
        }
    }
    console.log(lines.slice(start, end + 1).join('\n'));
} else {
    console.log("Not found");
}