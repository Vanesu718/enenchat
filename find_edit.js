const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf8');
const lines = content.split('\n');

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('function editCurrentContact') || lines[i].includes('function showContactDetail') || lines[i].includes('function editContact')) {
        console.log("Found:", lines[i]);
        console.log(lines.slice(i, i+30).join('\n'));
        console.log("------");
    }
}
