const fs = require('fs');

const content = fs.readFileSync('js/main.js', 'utf8');
const idx = content.indexOf('triggerAIReply');
if (idx === -1) {
    console.log("triggerAIReply not found");
} else {
    console.log("triggerAIReply found at:", idx);
    console.log(content.substring(idx, idx + 4000));
}
