const fs = require('fs');
const path = require('path');

// Step 1: Backup
const backupDir = path.join(__dirname, 'backup_v3');
if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir);
}
['js/main.js', 'index.html', 'css/chat.css', 'js/backup-system.js'].forEach(file => {
    if (fs.existsSync(file)) {
        fs.copyFileSync(file, path.join(backupDir, path.basename(file)));
    }
});
console.log("Backup completed.");
