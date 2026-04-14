const fs = require('fs');
const lines = fs.readFileSync('js/main.js', 'utf8').split('
');

lines.forEach((line, i) => {
    if (line.includes('stm.roundCount = (stm.roundCount || 0) + 1;')) {
        console.log(`Line ${i + 1}:`);
        console.log(lines.slice(Math.max(0, i - 5), Math.min(lines.length, i + 6)).join('
'));
        console.log('---');
    }
});