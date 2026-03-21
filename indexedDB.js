// IndexedDB 数据库管理模块
// 存储容量：50MB-500MB（根据浏览器不同）

const DB_NAME = 'OhoAppDB';
const DB_VERSION = 1;
const STORES = {
  images: 'images',      // 存储图片
  contacts: 'contacts',  // 存储联系人
  chats: 'chats',       // 存储聊天记录
  settings: 'settings'   // 存储设置
};

let db = null;
let initPromise = null;

// 初始化数据库
async function initDB() {
  if (db) return db;
  if (initPromise) return initPromise;
  
  initPromise = new Promise((resolve, reject) => {
    try {
      const idb = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
      if (!idb) {
        initPromise = null;
        reject(new Error('IndexedDB not supported'));
        return;
      }
      
      const request = idb.open(DB_NAME, DB_VERSION);
      
      request.onerror = (event) => {
        console.error('IndexedDB open error:', event.target.error);
        initPromise = null;
        reject(event.target.error || new Error('IndexedDB open failed'));
      };
      
      request.onsuccess = (event) => {
        db = event.target.result;
        
        db.onclose = () => {
          db = null;
          initPromise = null;
        };
        
        db.onerror = (e) => {
          console.error('IndexedDB error:', e.target.error);
        };
        
        resolve(db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // 创建图片存储
        if (!db.objectStoreNames.contains(STORES.images)) {
          const imageStore = db.createObjectStore(STORES.images, { keyPath: 'id' });
          imageStore.createIndex('type', 'type', { unique: false });
        }
        
        // 创建联系人存储
        if (!db.objectStoreNames.contains(STORES.contacts)) {
          db.createObjectStore(STORES.contacts, { keyPath: 'id' });
        }
        
        // 创建聊天记录存储
        if (!db.objectStoreNames.contains(STORES.chats)) {
          const chatStore = db.createObjectStore(STORES.chats, { keyPath: 'id' });
          chatStore.createIndex('contactId', 'contactId', { unique: false });
        }
        
        // 创建设置存储
        if (!db.objectStoreNames.contains(STORES.settings)) {
          db.createObjectStore(STORES.settings, { keyPath: 'key' });
        }
      };
    } catch (error) {
      console.error('IndexedDB init error:', error);
      initPromise = null;
      reject(error);
    }
  });
  return initPromise;
}

// 保存图片到 IndexedDB
async function saveImage(id, data, type = 'general') {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.images], 'readwrite');
    const store = transaction.objectStore(STORES.images);
    
    const request = store.put({
      id: id,
      data: data,
      type: type,
      timestamp: Date.now()
    });
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 从 IndexedDB 读取图片
async function getImage(id) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.images], 'readonly');
    const store = transaction.objectStore(STORES.images);
    const request = store.get(id);
    
    request.onsuccess = () => {
      const result = request.result;
      resolve(result ? result.data : null);
    };
    request.onerror = () => reject(request.error);
  });
}

// 删除图片
async function deleteImage(id) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.images], 'readwrite');
    const store = transaction.objectStore(STORES.images);
    const request = store.delete(id);
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 保存联系人到 IndexedDB
async function saveContact(contact) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.contacts], 'readwrite');
    const store = transaction.objectStore(STORES.contacts);
    const request = store.put(contact);
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 获取所有联系人
async function getAllContacts() {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.contacts], 'readonly');
    const store = transaction.objectStore(STORES.contacts);
    const request = store.getAll();
    
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
}

// 保存聊天记录
async function saveChatMessage(contactId, message) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.chats], 'readwrite');
    const store = transaction.objectStore(STORES.chats);
    
    const chatMessage = {
      id: `${contactId}_${Date.now()}_${Math.random()}`,
      contactId: contactId,
      ...message
    };
    
    const request = store.put(chatMessage);
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 获取某个联系人的聊天记录
async function getChatMessages(contactId) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.chats], 'readonly');
    const store = transaction.objectStore(STORES.chats);
    const index = store.index('contactId');
    const request = index.getAll(contactId);
    
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
}

// 保存设置
async function saveSetting(key, value) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.settings], 'readwrite');
    const store = transaction.objectStore(STORES.settings);
    const request = store.put({ key: key, value: value });
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 获取设置
async function getSetting(key) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.settings], 'readonly');
    const store = transaction.objectStore(STORES.settings);
    const request = store.get(key);
    
    request.onsuccess = () => {
      const result = request.result;
      resolve(result ? result.value : null);
    };
    request.onerror = () => reject(request.error);
  });
}

// 获取 IndexedDB 使用情况
async function getStorageInfo() {
  if (!navigator.storage || !navigator.storage.estimate) {
    return { usage: 0, quota: 0, percentage: 0 };
  }
  
  try {
    const estimate = await navigator.storage.estimate();
    const usage = estimate.usage || 0;
    const quota = estimate.quota || 0;
    const percentage = quota > 0 ? ((usage / quota) * 100).toFixed(2) : 0;
    
    return {
      usage: (usage / 1024 / 1024).toFixed(2) + ' MB',
      quota: (quota / 1024 / 1024).toFixed(2) + ' MB',
      percentage: percentage + '%'
    };
  } catch (e) {
    console.error('获取存储信息失败:', e);
    return { usage: 0, quota: 0, percentage: 0 };
  }
}

// 从 localStorage 迁移数据到 IndexedDB
async function migrateFromLocalStorage() {
  console.log('🔄 开始迁移数据到 IndexedDB...');
  
  try {
    let migratedCount = 0;
    
    // 获取所有 keys 避免在迭代时修改导致跳过
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      keys.push(localStorage.key(i));
    }
    
    // 迁移所有 localStorage 数据到 IndexedDB
    for (const key of keys) {
      if (!key) continue;
      
      const value = localStorage.getItem(key);
      if (!value) continue;
      
      // 判断是否为图片数据（base64）
      if (value.startsWith('data:image')) {
        await saveImage(key, value, 'image');
        localStorage.removeItem(key); // 释放空间
        console.log(`✅ 已迁移图片: ${key}`);
      } else {
        // 文本数据
        try {
          // 尝试解析 JSON
          const parsed = JSON.parse(value);
          await saveData(key, parsed);
        } catch {
          // 纯文本
          await saveData(key, value);
        }
        console.log(`✅ 已迁移数据: ${key}`);
      }
      
      migratedCount++;
    }
    
    // 标记迁移完成
    await saveSetting('migrated', true);
    await saveSetting('migratedAt', new Date().toISOString());
    await saveSetting('migratedCount', migratedCount);
    
    console.log(`✅ 数据迁移完成！共迁移 ${migratedCount} 项数据`);
    return true;
  } catch (e) {
    console.error('❌ 数据迁移失败:', e);
    return false;
  }
}

// 检查是否已迁移
async function checkMigration() {
  const migrated = await getSetting('migrated');
  return migrated === true;
}

// 保存通用数据（用于朋友圈、世界书等）
async function saveData(key, data) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.settings], 'readwrite');
    const store = transaction.objectStore(STORES.settings);
    const request = store.put({ 
      key: key, 
      value: data,
      timestamp: Date.now()
    });
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 获取通用数据
async function getData(key) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.settings], 'readonly');
    const store = transaction.objectStore(STORES.settings);
    const request = store.get(key);
    
    request.onsuccess = () => {
      const result = request.result;
      resolve(result ? result.value : null);
    };
    request.onerror = () => reject(request.error);
  });
}

// 删除数据
async function deleteData(key) {
  if (!db) await initDB();
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.settings], 'readwrite');
    const store = transaction.objectStore(STORES.settings);
    const request = store.delete(key);
    
    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

// 导出函数
window.IndexedDBManager = {
  initDB,
  saveImage,
  getImage,
  deleteImage,
  saveContact,
  getAllContacts,
  saveChatMessage,
  getChatMessages,
  saveSetting,
  getSetting,
  saveData,
  getData,
  deleteData,
  getStorageInfo,
  migrateFromLocalStorage,
  checkMigration
};
