const fs = require('fs');
const path = require('path');

const historyDir = 'C:\\Users\\Administrator\\AppData\\Roaming\\Code\\User\\History';
const targetFile = 'index.html';

function findBackups() {
    if (!fs.existsSync(historyDir)) return;
    const dirs = fs.readdirSync(historyDir);
    let backups = [];

    for (const d of dirs) {
        const dirPath = path.join(historyDir, d);
        const stat = fs.statSync(dirPath);
        if (stat.isDirectory()) {
            const entriesPath = path.join(dirPath, 'entries.json');
            if (fs.existsSync(entriesPath)) {
                try {
                    const content = JSON.parse(fs.readFileSync(entriesPath, 'utf8'));
                    if (content.resource && content.resource.endsWith(targetFile)) {
                        for (const entry of content.entries) {
                            const entryPath = path.join(dirPath, entry.id);
                            if (fs.existsSync(entryPath)) {
                                const entryStat = fs.statSync(entryPath);
                                backups.push({
                                    path: entryPath,
                                    mtime: entryStat.mtimeMs,
                                    mtimeStr: entryStat.mtime.toLocaleString(),
                                    size: entryStat.size,
                                    source: content.resource
                                });
                            }
                        }
                    }
                } catch (e) {
                    // ignore
                }
            }
        }
    }

    backups.sort((a, b) => b.mtime - a.mtime);
    
    console.log(`Found ${backups.length} backups for ${targetFile}:`);
    for (let i = 0; i < Math.min(20, backups.length); i++) {
        const b = backups[i];
        console.log(`${b.mtimeStr} - ${b.size} bytes - ${b.path}`);
    }
}

findBackups();
