const fs = require('fs');
const path = require('path');

const historyDir = 'C:\\Users\\Administrator\\AppData\\Roaming\\Code\\User\\History';
const destDir = 'c:\\Users\\Administrator\\Desktop\\111';

console.log('正在扫描VS Code本地缓存找回代码...');

if (!fs.existsSync(historyDir)) {
    console.log(`找不到目录: ${historyDir}`);
    process.exit(1);
}

const candidates = [];

function walk(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const filepath = path.join(dir, file);
        const stat = fs.statSync(filepath);
        if (stat.isDirectory()) {
            walk(filepath);
        } else if (file !== 'entries.json') {
            if (stat.mtimeMs > Date.now() - 86400000) {
                candidates.push({ mtime: stat.mtimeMs, filepath });
            }
        }
    }
}

walk(historyDir);
candidates.sort((a, b) => b.mtime - a.mtime);

let foundCount = 0;
for (const cand of candidates) {
    if (foundCount >= 5) break;
    try {
        const content = fs.readFileSync(cand.filepath, 'utf8');
        if (content.includes('论坛') && content.includes('<html') && content.includes('面具')) {
            const recoverPath = path.join(destDir, `index_recovered_${foundCount}.html`);
            fs.writeFileSync(recoverPath, content, 'utf8');
            console.log(`成功找到备份! 已恢复为 ${recoverPath}, 备份时间: ${new Date(cand.mtime).toLocaleString()}`);
            foundCount++;
        }
    } catch (e) {
        // ignore
    }
}

if (foundCount === 0) {
    console.log('未能找到包含论坛和面具代码的备份。');
} else {
    console.log('扫描完成。');
}
