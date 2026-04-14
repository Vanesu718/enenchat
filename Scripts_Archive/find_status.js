const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf8');

const lines = content.split('\n');
const targets = ['地点', '心情', '心声', '好感'];
lines.forEach((line, i) => {
    if (targets.some(t => line.includes(t))) {
        console.log(`Line ${i + 1}: ${line}`);
    }
});
