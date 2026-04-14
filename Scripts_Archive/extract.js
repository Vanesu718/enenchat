const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf8');
const start = content.indexOf('async function triggerAIReply');
const end = content.indexOf('function stopAIReply', start);
const extracted = content.substring(start, end);
fs.writeFileSync('temp_extract.txt', extracted);
