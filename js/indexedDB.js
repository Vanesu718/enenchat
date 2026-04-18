// IndexedDB 数据库管理模块 - Dexie.js 版本
// 存储容量：50MB-500MB（根据浏览器不同）
// 使用 Dexie.js v3.2.1 封装 IndexedDB

const DB_NAME = 'OhoAppDB';
const OLD_DB_NAME = 'OhoAppDB'; // 旧库名（用于迁移检测）

// ========== Dexie 数据库定义 ==========
const db = new Dexie(DB_NAME);

// 从 version(2) 开始，避免与旧原生 IndexedDB version(1) 冲突
db.version(2).stores({
  images: 'id, type',           // 存储图片
  contacts: 'id',               // 存储联系人
  chats: 'id, contactId',       // 存储聊天记录
  settings: 'key'               // 存储设置/通用数据
});

// 暴露到 window 供 backup-system.js 使用
window.db = db;

let dbReady = false;
let dbReadyPromise = null;

// ========== 初始化数据库（含旧库迁移） ==========
async function initDB() {
  if (dbReady) return db;
  if (dbReadyPromise) return dbReadyPromise;

  dbReadyPromise = (async () => {
    try {
      await db.open();
      console.log('✅ Dexie 数据库已打开:', DB_NAME);

      // 检查是否需要从旧原生 IndexedDB 迁移数据
      await migrateFromOldNativeDB();

      dbReady = true;
      return db;
    } catch (error) {
      console.error('❌ Dexie 数据库打开失败:', error);
      dbReadyPromise = null;
      throw error;
    }
  })();

  return dbReadyPromise;
}

// ========== 从旧原生 IndexedDB 迁移数据到 Dexie ==========
async function migrateFromOldNativeDB() {
  // 检查是否已经迁移过
  try {
    const migrationFlag = await db.settings.get('_dexie_migration_done');
    if (migrationFlag && migrationFlag.value === true) {
      return; // 已迁移，跳过
    }
  } catch (e) {
    // settings 表可能还没数据，继续
  }

  console.log('🔄 检查旧原生 IndexedDB 数据...');

  try {
    // 用原生 API 尝试打开旧库（version 1）
    const oldData = await readOldNativeDB();

    if (!oldData) {
      console.log('ℹ️ 没有旧库数据需要迁移');
      await db.settings.put({ key: '_dexie_migration_done', value: true, timestamp: Date.now() });
      return;
    }

    const { images: oldImages, contacts: oldContacts, chats: oldChats, settings: oldSettings } = oldData;

    let totalOld = oldImages.length + oldContacts.length + oldChats.length + oldSettings.length;
    console.log(`📊 旧库数据总条数: ${totalOld}`);

    if (totalOld === 0) {
      console.log('ℹ️ 旧库无数据，标记迁移完成');
      await db.settings.put({ key: '_dexie_migration_done', value: true, timestamp: Date.now() });
      return;
    }

    // 用 Dexie bulkPut 写入新库
    if (oldImages.length > 0) {
      await db.images.bulkPut(oldImages);
      console.log(`✅ 迁移图片: ${oldImages.length} 条`);
    }
    if (oldContacts.length > 0) {
      await db.contacts.bulkPut(oldContacts);
      console.log(`✅ 迁移联系人: ${oldContacts.length} 条`);
    }
    if (oldChats.length > 0) {
      await db.chats.bulkPut(oldChats);
      console.log(`✅ 迁移聊天记录: ${oldChats.length} 条`);
    }
    if (oldSettings.length > 0) {
      await db.settings.bulkPut(oldSettings);
      console.log(`✅ 迁移设置: ${oldSettings.length} 条`);
    }

    // 迁移后验证数据条数
    const newImageCount = await db.images.count();
    const newContactCount = await db.contacts.count();
    const newChatCount = await db.chats.count();
    const newSettingCount = await db.settings.count();
    const totalNew = newImageCount + newContactCount + newChatCount + newSettingCount;

    console.log(`📊 迁移后新库数据总条数: ${totalNew} (旧库: ${totalOld})`);

    if (totalNew >= totalOld) {
      // 标记迁移完成（不删除旧库）
      await db.settings.put({ key: '_dexie_migration_done', value: true, timestamp: Date.now() });
      await db.settings.put({ key: '_migration_info', value: {
        migratedAt: new Date().toISOString(),
        oldCount: totalOld,
        newCount: totalNew
      }, timestamp: Date.now() });
      console.log('✅ 数据迁移完成！旧库保留不删除。');
    } else {
      console.warn('⚠️ 迁移后数据条数不一致，旧库保留。旧:', totalOld, '新:', totalNew);
    }
  } catch (e) {
    console.error('❌ 旧库迁移过程出错:', e);
    // 迁移失败不影响新库使用
  }
}

// ========== 用原生 IndexedDB API 读取旧库数据 ==========
function readOldNativeDB() {
  return new Promise((resolve) => {
    const idb = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
    if (!idb) {
      resolve(null);
      return;
    }

    // 尝试以 version 1 打开旧库
    const request = idb.open(DB_NAME, 1);

    request.onerror = () => {
      console.log('ℹ️ 无法打开旧库（可能不存在）');
      resolve(null);
    };

    request.onupgradeneeded = (event) => {
      // 如果触发了 onupgradeneeded，说明旧库不存在（正在创建 version 1）
      // 取消事务，不创建旧库
      event.target.transaction.abort();
      resolve(null);
    };

    request.onsuccess = (event) => {
      const oldDb = event.target.result;
      const storeNames = Array.from(oldDb.objectStoreNames);

      if (storeNames.length === 0) {
        oldDb.close();
        resolve(null);
        return;
      }

      const result = { images: [], contacts: [], chats: [], settings: [] };
      const targetStores = ['images', 'contacts', 'chats', 'settings'];
      const storesToRead = targetStores.filter(s => storeNames.includes(s));

      if (storesToRead.length === 0) {
        oldDb.close();
        resolve(null);
        return;
      }

      let completed = 0;

      try {
        const tx = oldDb.transaction(storesToRead, 'readonly');

        for (const storeName of storesToRead) {
          const store = tx.objectStore(storeName);
          const getAllReq = store.getAll();

          getAllReq.onsuccess = () => {
            result[storeName] = getAllReq.result || [];
            completed++;
            if (completed === storesToRead.length) {
              oldDb.close();
              resolve(result);
            }
          };

          getAllReq.onerror = () => {
            completed++;
            if (completed === storesToRead.length) {
              oldDb.close();
              resolve(result);
            }
          };
        }

        tx.onerror = () => {
          oldDb.close();
          resolve(result);
        };
      } catch (e) {
        oldDb.close();
        resolve(null);
      }
    };
  });
}

// ========== 图片操作 ==========
async function saveImage(id, data, type = 'general') {
  await initDB();
  return db.images.put({
    id: id,
    data: data,
    type: type,
    timestamp: Date.now()
  });
}

async function getImage(id) {
  await initDB();
  const result = await db.images.get(id);
  return result ? result.data : null;
}

async function deleteImage(id) {
  await initDB();
  return db.images.delete(id);
}

// ========== 联系人操作 ==========
async function saveContact(contact) {
  await initDB();
  return db.contacts.put(contact);
}

async function getAllContacts() {
  await initDB();
  return db.contacts.toArray();
}

// ========== 聊天记录操作 ==========
async function saveChatMessage(contactId, message) {
  await initDB();
  const chatMessage = {
    id: `${contactId}_${Date.now()}_${Math.random()}`,
    contactId: contactId,
    ...message
  };
  return db.chats.put(chatMessage);
}

async function getChatMessages(contactId) {
  await initDB();
  return db.chats.where('contactId').equals(contactId).toArray();
}

// ========== 设置操作 ==========
async function saveSetting(key, value) {
  await initDB();
  return db.settings.put({ key: key, value: value });
}

async function getSetting(key) {
  await initDB();
  const result = await db.settings.get(key);
  return result ? result.value : null;
}

// ========== 通用数据操作 ==========
async function saveData(key, data) {
  await initDB();
  return db.settings.put({
    key: key,
    value: data,
    timestamp: Date.now()
  });
}

async function getData(key) {
  await initDB();
  const result = await db.settings.get(key);
  return result ? result.value : null;
}

async function deleteData(key) {
  await initDB();
  return db.settings.delete(key);
}

// ========== 存储信息 ==========
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

// ========== 从 localStorage 迁移数据到 IndexedDB ==========
async function migrateFromLocalStorage() {
  console.log('🔄 开始迁移 localStorage 数据到 IndexedDB...');

  try {
    await initDB();
    let migratedCount = 0;

    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      keys.push(localStorage.key(i));
    }

    for (const key of keys) {
      if (!key) continue;
      const value = localStorage.getItem(key);
      if (!value) continue;

      if (value.startsWith('data:image')) {
        await saveImage(key, value, 'image');
        localStorage.removeItem(key);
        console.log(`✅ 已迁移图片: ${key}`);
      } else {
        try {
          const parsed = JSON.parse(value);
          await saveData(key, parsed);
        } catch {
          await saveData(key, value);
        }
        console.log(`✅ 已迁移数据: ${key}`);
      }

      migratedCount++;
    }

    await saveSetting('migrated', true);
    await saveSetting('migratedAt', new Date().toISOString());
    await saveSetting('migratedCount', migratedCount);

    console.log(`✅ localStorage 数据迁移完成！共迁移 ${migratedCount} 项`);
    return true;
  } catch (e) {
    console.error('❌ localStorage 数据迁移失败:', e);
    return false;
  }
}

// 检查是否已迁移
async function checkMigration() {
  await initDB();
  const migrated = await getSetting('migrated');
  return migrated === true;
}

// ========== 导出接口（保持 window.IndexedDBManager 不变） ==========
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
