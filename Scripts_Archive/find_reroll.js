const fs = require('fs'); const content = fs.readFileSync('js/main.js', 'utf8'); const m = content.match(/async function handleReRoll[\s\S]*?^}/m); if (m) console.log(m[0]);
