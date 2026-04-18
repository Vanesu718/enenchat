/**
 * 备份系统核心逻辑 - 支持分批导出与压缩
 * 使用 Dexie.js API 操作 IndexedDB
 */

// 更新备份进度条
function updateBackupProgress(text, percent) {
    const progressContainer = document.getElementById('backupProgress');
    const progressText = document.getElementById('backupProgressText');
    const progressBar = document.getElementById('backupProgressBar');
    
    if (progressContainer && progressText && progressBar) {
        progressContainer.style.display = 'block';
        progressText.textContent = text;
        progressBar.style.width = percent + '%';
        
        if (percent >= 100) {
            setTimeout(() => {
                progressContainer.style.display = 'none';
            }, 2000);
        }
    }
}

// 统一的导出函数
async function exportBackup(type = 'chat') {
    try {
        updateBackupProgress('准备导出...', 0);
        const prefix = type === 'chat' ? 'OHO_ChatOnly_Backup' : 'OHO_Full_Backup';
        const filename = `${prefix}_.json.gz`;

        if (type === 'chat') {
            await exportChatBackup(filename);
        } else {
            await exportFullBackup(filename);
        }
    } catch (error) {
        console.error('备份失败:', error);
        alert('备份失败，请查看控制台错误信息。\n' + error.message);
        updateBackupProgress('备份失败', 0);
    }
}

// 辅助函数：用 Dexie API 分批读取表数据
async function streamDexieTable(tableName, callback, batchSize = 200) {
    const dexieDb = window.db;
    if (!dexieDb || !dexieDb[tableName]) {
        console.warn('表不存在:', tableName);
        return 0;
    }

    const totalCount = await dexieDb[tableName].count();
    let count = 0;

    await dexieDb[tableName].each((item) => {
        callback(item, count, totalCount);
        count++;
    });

    return count;
}

// 辅助函数：流式写入JSON数组
class JsonStreamWriter {
    constructor() {
        this.chunks = [];
        this.first = true;
    }
    
    startObject() { this.chunks.push('{'); this.first = true; }
    endObject() { this.chunks.push('}'); this.first = false; }
    
    startArray(key) {
        this.addKey(key);
        this.chunks.push('[');
        this.first = true;
    }
    endArray() { this.chunks.push(']'); this.first = false; }
    
    addKey(key) {
        if (!this.first) this.chunks.push(',');
        this.chunks.push(JSON.stringify(key) + ':');
        this.first = true;
    }
    
    addValue(value) {
        if (!this.first) this.chunks.push(',');
        this.chunks.push(JSON.stringify(value));
        this.first = false;
    }
    
    addKeyValue(key, value) {
        this.addKey(key);
        this.chunks.push(JSON.stringify(value));
        this.first = false;
    }

    addRawKeyValue(key, rawValueStr) {
        this.addKey(key);
        this.chunks.push(rawValueStr);
        this.first = false;
    }
    
    getChunks() { return this.chunks; }
}

// ================== 仅聊天备份 ==================
async function exportChatBackup(filename) {
    updateBackupProgress('正在准备仅聊天备份...', 5);
    
    const dexieDb = window.db;
    if (!dexieDb) throw new Error('数据库尚未初始化');

    const writer = new JsonStreamWriter();
    writer.startObject();
    
    // Meta
    writer.addKeyValue('meta', {
        version: '2.0',
        type: 'chat_only',
        exportTime: new Date().toISOString()
    });

    // LocalStorage
    updateBackupProgress('正在读取基础数据与设置...', 10);
    writer.startObject('localStorage');
    
    const baseKeys = [
        'userProfile', 'contacts', 'groups', 
        'chatRecords', 'chatSettings', 
        'worldBook', 'worldBookEntries',
        'ltmAutoEnabled', 'stmAutoEnabled', 'stmWindowSize', 'ltmPrompt', 'stmPrompt',
        'customEmojis', 'customWritingStyles', 'THEME_CLASS'
    ];
    
    const keysToExport = new Set(baseKeys);
    
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && (key.startsWith('CHAT_SETTINGS_') || key.startsWith('STATUS_') || key.startsWith('bg_') || key.startsWith('group_bg_'))) {
            keysToExport.add(key);
        }
    }

    for (const key of keysToExport) {
        const val = localStorage.getItem(key);
        if (val !== null) {
            writer.addKeyValue(key, val);
        }
    }
    writer.endObject();

    // IndexedDB - 使用 Dexie API
    updateBackupProgress('正在处理 IndexedDB 核心数据...', 30);
    writer.startObject('indexedDB');
    
    // Dexie 表名列表
    const tableNames = dexieDb.tables.map(t => t.name);
    const storesToExport = ['images', 'contacts', 'chats', 'settings'];
    const actualTables = storesToExport.filter(s => tableNames.includes(s));
    
    for (let i = 0; i < actualTables.length; i++) {
        const tableName = actualTables[i];
        writer.startArray(tableName);
        
        let count = 0;
        const totalCount = await dexieDb[tableName].count();
        
        await dexieDb[tableName].each((item) => {
            // 聊天备份中过滤图片
            if (tableName === 'chats' && item.type === 'image') {
                item = { ...item, type: 'text', content: '[图片已在仅聊天备份中省略]' };
            }
            writer.addValue(item);
            
            count++;
            if (count % 50 === 0) {
                const basePercent = 30 + (i / actualTables.length) * 50;
                const subPercent = (count / Math.max(totalCount, 1)) * (50 / actualTables.length);
                const percent = basePercent + subPercent;
                updateBackupProgress('正在处理 ' + tableName + ' ' + count + '/' + totalCount + '...', percent);
            }
        });
        
        writer.endArray();
    }

    writer.endObject(); // end indexedDB
    writer.endObject(); // end root

    // 压缩并下载
    updateBackupProgress('正在组合并压缩数据，请稍候...', 80);
    await new Promise(resolve => setTimeout(resolve, 50));
    
    const jsonStr = writer.getChunks().join('');
    
    let finalBlob;
    if (window.pako) {
        const compressed = pako.gzip(jsonStr);
        finalBlob = new Blob([compressed], { type: 'application/gzip' });
    } else {
        console.warn('pako.js 未加载，回退为普通 JSON 下载');
        finalBlob = new Blob([jsonStr], { type: 'application/json' });
        filename = filename.replace('.gz', '');
    }
    
    downloadBlob(finalBlob, filename);
    updateBackupProgress('仅聊天备份完成！', 100);
}

// ================== 全局备份 (流式压缩方案) ==================
async function exportFullBackup(filename) {
    updateBackupProgress('正在准备全局备份...', 5);
    
    const dexieDb = window.db;
    if (!dexieDb) throw new Error('数据库尚未初始化');

    const writer = new JsonStreamWriter();
    writer.startObject();
    
    // Meta
    writer.addKeyValue('meta', {
        version: '2.0',
        type: 'full',
        exportTime: new Date().toISOString()
    });

    // LocalStorage
    updateBackupProgress('正在导出系统设置...', 10);
    writer.startObject('localStorage');
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        writer.addKeyValue(key, localStorage.getItem(key));
    }
    writer.endObject();

    // IndexedDB - 使用 Dexie API
    writer.startObject('indexedDB');
    const tableNames = dexieDb.tables.map(t => t.name);
    
    for (let i = 0; i < tableNames.length; i++) {
        const tableName = tableNames[i];
        writer.startArray(tableName);
        
        let count = 0;
        const totalCount = await dexieDb[tableName].count();
        
        await dexieDb[tableName].each((item) => {
            writer.addValue(item);
            count++;
            if (count % 50 === 0) {
                const basePercent = 15 + (i / tableNames.length) * 70;
                const subPercent = (count / Math.max(totalCount, 1)) * (70 / tableNames.length);
                const percent = basePercent + subPercent;
                updateBackupProgress('正在处理 ' + tableName + ' ' + count + '/' + totalCount + '...', percent);
            }
        });
        
        writer.endArray();
    }
    writer.endObject(); // end indexedDB
    writer.endObject(); // end root

    // 组合 chunks 并压缩
    updateBackupProgress('正在组合并压缩数据，这可能需要一些时间...', 90);
    await new Promise(resolve => setTimeout(resolve, 50));
    
    const jsonStr = writer.getChunks().join('');
    
    let finalBlob;
    if (window.pako) {
        const compressed = pako.gzip(jsonStr);
        finalBlob = new Blob([compressed], { type: 'application/gzip' });
    } else {
        console.warn('pako 未加载，回退为普通JSON');
        finalBlob = new Blob([jsonStr], { type: 'application/json' });
        filename = filename.replace('.gz', '');
    }

    downloadBlob(finalBlob, filename);
    updateBackupProgress('全局备份完成！', 100);
}

// ================== 下载辅助函数 ==================
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

// ================== 导入恢复 ==================
async function importBackup(fileInput) {
    const file = fileInput.files[0];
    if (!file) return;

    try {
        updateBackupProgress('正在读取备份文件...', 10);
        let text = '';
        
        // 检查是否是 gzip 压缩的
        if (file.name.endsWith('.gz') || file.type === 'application/gzip') {
            if (!window.pako) throw new Error('缺少 pako.js，无法解压备份文件');
            const arrayBuffer = await file.arrayBuffer();
            updateBackupProgress('正在解压备份文件...', 30);
            const decompressed = pako.ungzip(new Uint8Array(arrayBuffer), { to: 'string' });
            text = decompressed;
        } else {
            text = await file.text();
        }

        updateBackupProgress('正在解析数据...', 40);
        const data = JSON.parse(text);
        
        const isFull = data.meta && data.meta.type === 'full';
        
        if (confirm(`检测到 ${isFull ? '全局' : '仅聊天'} 备份。导入将覆盖当前对应数据，是否继续？`)) {
            await performRestore(data, isFull);
        }
    } catch (e) {
        console.error('导入失败:', e);
        alert('导入失败: ' + e.message);
        updateBackupProgress('导入失败', 0);
    } finally {
        fileInput.value = ''; // reset
    }
}

async function performRestore(data, isFull) {
    updateBackupProgress('正在恢复 LocalStorage 设置...', 50);
    
    const dexieDb = window.db;
    
    // 恢复 localStorage
    if (data.localStorage) {
        if (isFull) {
            const ohoActivated = localStorage.getItem('OHO_ACTIVATED');
            localStorage.clear();
            if (ohoActivated) localStorage.setItem('OHO_ACTIVATED', ohoActivated);
        }
        for (const [key, value] of Object.entries(data.localStorage)) {
            localStorage.setItem(key, value);
        }
    }

    // 恢复 IndexedDB - 使用 Dexie API
    if (data.indexedDB && dexieDb) {
        const storeNames = Object.keys(data.indexedDB);
        const tableNames = dexieDb.tables.map(t => t.name);
        
        for (let i = 0; i < storeNames.length; i++) {
            const storeName = storeNames[i];
            const records = data.indexedDB[storeName];
            
            // 检查 Dexie 中是否有这个表
            if (!tableNames.includes(storeName)) {
                console.warn('跳过不存在的表:', storeName);
                continue;
            }
            
            if (isFull || !['settings', 'images'].includes(storeName)) {
                updateBackupProgress(`正在清理 ${storeName} 表...`, 60 + (i / storeNames.length) * 10);
                await dexieDb[storeName].clear();
            } else {
                updateBackupProgress(`正在更新 ${storeName} 表...`, 60 + (i / storeNames.length) * 10);
            }
            
            const total = records.length;
            // 分批写入，使用 Dexie bulkPut
            const BATCH_SIZE = 500;
            for (let j = 0; j < total; j += BATCH_SIZE) {
                const batch = records.slice(j, j + BATCH_SIZE);
                updateBackupProgress(`正在恢复 ${storeName} (${Math.min(j + BATCH_SIZE, total)}/${total})...`, 70 + (i / storeNames.length) * 20 + (j/total)*20);
                await dexieDb[storeName].bulkPut(batch);
            }
        }
    }

    updateBackupProgress('数据恢复完成！即将刷新...', 100);
    setTimeout(() => {
        alert('导入成功，点击确定刷新页面。');
        location.reload();
    }, 500);
}
