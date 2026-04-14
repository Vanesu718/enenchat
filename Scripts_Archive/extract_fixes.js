const fs = require('fs');

const file = 'js/main.js';
let code = fs.readFileSync(file, 'utf8');

const triggerMatch = code.match(/async function triggerAIReply[\s\S]*?(?=async function \w|function \w|$)/);
if (triggerMatch) {
    fs.writeFileSync('triggerAIReply_temp.js', triggerMatch[0]);
    console.log('Exported triggerAIReply to triggerAIReply_temp.js');
}

const imgClickMatch = code.match(/function viewFullImage[\s\S]*?\}|document\.addEventListener\('click'[\s\S]*?(?=\}\);)\}\);/g);
if (imgClickMatch) {
    fs.writeFileSync('imgClick_temp.js', imgClickMatch.join('\n\n'));
    console.log('Exported imgClick to imgClick_temp.js');
}
