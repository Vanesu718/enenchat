/**
 * 澶囦唤绯荤粺鏍稿績閫昏緫 - 鏀寔鍒嗘壒瀵煎嚭涓庡帇缂?
 */

// 鏇存柊澶囦唤杩涘害鏉?
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

// 缁熶竴鐨勫鍑哄嚱鏁?
async function exportBackup(type = 'chat') {
    try {
        updateBackupProgress('鍑嗗瀵煎嚭...', 0);
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const prefix = type === 'chat' ? 'OHO_ChatOnly_Backup' : 'OHO_Full_Backup';
        const filename = `${prefix}_.json.gz`;

        if (type === 'chat') {
            await exportChatBackup(filename);
        } else {
            await exportFullBackup(filename);
        }
    } catch (error) {
        console.error('澶囦唤澶辫触:', error);
        alert('澶囦唤澶辫触锛岃鏌ョ湅鎺у埗鍙伴敊璇俊鎭€俓n' + error.message);
        updateBackupProgress('澶囦唤澶辫触', 0);
    }
}

// 杈呭姪鍑芥暟锛氬垎鎵硅鍙朓ndexedDB涓殑琛?
function streamObjectStore(db, storeName, callback, batchSize = 200) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([storeName], 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.openCursor();
        let count = 0;
        let totalCount = 0;
        
        // 鑾峰彇鎬绘暟浠ヨ绠楄繘搴?
        const countRequest = store.count();
        countRequest.onsuccess = () => {
            totalCount = countRequest.result;
        };

        request.onsuccess = async (event) => {
            const cursor = event.target.result;
            if (cursor) {
                await callback(cursor.value, count, totalCount);
                count++;
                cursor.continue();
            } else {
                resolve(count);
            }
        };
        request.onerror = (event) => reject(event.target.error);
    });
}

// 杈呭姪鍑芥暟锛氭祦寮忓啓鍏SON鏁扮粍
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
        this.first = true; // 鏁扮粍鎴栧璞″紑濮嬪悗
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

// ================== 浠呰亰澶╁浠?==================
async function exportChatBackup(filename) {
    updateBackupProgress('姝ｅ湪璇诲彇鑱旂郴浜轰笌鍩虹鏁版嵁...', 10);
    
    const exportData = {
        meta: {
            version: '2.0',
            type: 'chat_only',
            exportTime: new Date().toISOString()
        },
        localStorage: {},
        indexedDB: {}
    };

    // 1. 璇诲彇蹇呴』鐨?localStorage
    const keysToExport = [
        'userProfile', 'contacts', 'groups', 
        'chatRecords', 'chatSettings', 
        'worldBook', 'worldBookEntries',
        'ltmAutoEnabled', 'stmAutoEnabled', 'stmWindowSize', 'ltmPrompt', 'stmPrompt'
    ];
    
    keysToExport.forEach(key => {
        const val = localStorage.getItem(key);
        if (val) {
            exportData.localStorage[key] = val;
        }
    });

    updateBackupProgress('姝ｅ湪澶勭悊 IndexedDB 璁板繂鏁版嵁...', 30);
    // 2. 璇诲彇鍏宠仈鐨?IndexedDB
    const db = window.db;
    if (!db) {
        throw new Error('鏁版嵁搴撳皻鏈垵濮嬪寲');
    }

    const storesToExport = ['chatRecords', 'memory'];
    
    for (const storeName of storesToExport) {
        if (!db.objectStoreNames.contains(storeName)) continue;
        
        exportData.indexedDB[storeName] = [];
        await streamObjectStore(db, storeName, async (item, count, total) => {
            // 过滤图片，替换为提示文字
            if (storeName === 'chatRecords') {
                if (item.type === 'image') {
                    item.type = 'text';
                    item.content = '[图片已在仅聊天备份中省略]';
                }
            }
            exportData.indexedDB[storeName].push(item);
            
            if (count % 50 === 0) {
                const percent = 30 + (count / Math.max(total, 1)) * 40;
                updateBackupProgress('正在处理 ' + count + '/' + total + '...', percent);
            }
        });
    }

    // 3. 压缩并下载
    updateBackupProgress('正在压缩数据，请稍候...', 80);
    const jsonStr = JSON.stringify(exportData);
    
    // 使用 pako 压缩
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

// ================== 鍏ㄥ眬澶囦唤 (娴佸紡鍘嬬缉鏂规) ==================
async function exportFullBackup(filename) {
    updateBackupProgress('姝ｅ湪鍑嗗鍏ㄥ眬澶囦唤...', 5);
    
    const db = window.db;
    if (!db) throw new Error('鏁版嵁搴撳皻鏈垵濮嬪寲');

    const writer = new JsonStreamWriter();
    writer.startObject();
    
    // Meta
    writer.addKeyValue('meta', {
        version: '2.0',
        type: 'full',
        exportTime: new Date().toISOString()
    });

    // LocalStorage
    updateBackupProgress('姝ｅ湪瀵煎嚭绯荤粺璁剧疆...', 10);
    writer.startObject('localStorage');
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        writer.addKeyValue(key, localStorage.getItem(key));
    }
    writer.endObject();

    // IndexedDB
    writer.startObject('indexedDB');
    const storeNames = Array.from(db.objectStoreNames);
    
    for (let i = 0; i < storeNames.length; i++) {
        const storeName = storeNames[i];
        writer.startArray(storeName);
        
        await streamObjectStore(db, storeName, async (item, count, total) => {
            writer.addValue(item);
            if (count % 50 === 0) {
                const basePercent = 15 + (i / storeNames.length) * 70;
                const subPercent = (count / Math.max(total, 1)) * (70 / storeNames.length);
                const percent = basePercent + subPercent;
                updateBackupProgress('正在处理 ' + count + '/' + total + '...', percent);
            }
        });
        
        writer.endArray();
    }
    writer.endObject(); // end indexedDB
    writer.endObject(); // end root

    // 组合 chunks 并压缩
    updateBackupProgress('正在组合并压缩数据，这可能需要一些时间...', 90);
    
    // 延迟以让 UI 更新
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
    
    // 鎭㈠ localStorage
    if (data.localStorage) {
        if (isFull) {
            localStorage.clear();
        }
        for (const [key, value] of Object.entries(data.localStorage)) {
            localStorage.setItem(key, value);
        }
    }

    // 鎭㈠ IndexedDB
    if (data.indexedDB && window.db) {
        const storeNames = Object.keys(data.indexedDB);
        
        for (let i = 0; i < storeNames.length; i++) {
            const storeName = storeNames[i];
            const records = data.indexedDB[storeName];
            
            if (!window.db.objectStoreNames.contains(storeName)) continue;
            
            updateBackupProgress(`正在清理 ${storeName} 表...`, 60 + (i / storeNames.length) * 10);
            await clearObjectStore(window.db, storeName);
            
            const total = records.length;
            // 鍒嗘壒鍐欏叆锛岄伩鍏嶄竴娆℃€ц繃澶т簨鍔?
            const BATCH_SIZE = 500;
            for (let j = 0; j < total; j += BATCH_SIZE) {
            const batch = records.slice(j, j + BATCH_SIZE);
            updateBackupProgress(`正在恢复 ${storeName} (${Math.min(j + BATCH_SIZE, total)}/${total})...`, 70 + (i / storeNames.length) * 20 + (j/total)*20);
            await putBatchToObjectStore(window.db, storeName, batch);
            }
        }
    }

    updateBackupProgress('数据恢复完成！即将刷新...', 100);
    setTimeout(() => {
        alert('导入成功，点击确定刷新页面。');
        location.reload();
    }, 500);
}

function clearObjectStore(db, storeName) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const req = store.clear();
        req.onsuccess = () => resolve();
        req.onerror = (e) => reject(e.target.error);
    });
}

function putBatchToObjectStore(db, storeName, items) {
    return new Promise((resolve, reject) => {
        const tx = db.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        
        tx.oncomplete = () => resolve();
        tx.onerror = (e) => reject(e.target.error);
        
        for (const item of items) {
            store.put(item);
        }
    });
}
