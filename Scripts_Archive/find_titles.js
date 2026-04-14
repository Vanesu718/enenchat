const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf-8');
const titles = content.match(/title="[^"]+"/g);
console.log(titles);
