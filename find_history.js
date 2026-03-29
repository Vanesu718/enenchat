const fs = require('fs');
const path = require('path');

const historyDir = 'C:\\Users\\Administrator\\AppData\\Roaming\\Code\\User\\History';
let allFiles = [];

function walkDir(dir) {
    if (!fs.existsSync(dir)) return;
    const files = fs.readdirSync(dir);
    for (const f of files) {
        const fullPath = path.join(dir, f);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
            walkDir(fullPath);
        } else if (f !== 'entries.json') {
            allFiles.push({
                path: fullPath,
                mtime: stat.mtimeMs,
                mtimeStr: stat.mtime.toLocaleString(),
                size: stat.size
            });
        }
    }
}

walkDir(historyDir);
allFiles.sort((a, b) => b.mtime - a.mtime);

for (let i = 0; i < Math.min(30, allFiles.length); i++) {
    const f = allFiles[i];
    console.log(`${f.path} - ${f.mtimeStr} - ${f.size} bytes`);
}
