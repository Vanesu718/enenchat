// 统一存储管理器 - 自动使用 IndexedDB，向后兼容 localStorage
// 这个模块提供与 localStorage 相同的 API，但底层使用 IndexedDB

class StorageManager {
  constructor() {
    this.ready = false;
    this.initPromise = null;
  }

  // 初始化
  async init() {
    if (this.ready) return true;
    if (this.initPromise) return this.initPromise;
    
    this.initPromise = (async () => {
      try {
        await IndexedDBManager.initDB();
        
        // 检查是否需要迁移
        try {
          const migrated = await IndexedDBManager.checkMigration();
          if (!migrated) {
            console.log('🔄 检测到 localStorage 数据，开始自动迁移...');
            const success = await IndexedDBManager.migrateFromLocalStorage();
            if (success) {
              // 迁移成功后清空 localStorage
              console.log('🧹 清理 localStorage...');
              localStorage.clear();
              console.log('✅ 迁移完成，localStorage 已清空');
            }
          }
        } catch (migrationError) {
          console.error('迁移检查失败，跳过迁移:', migrationError);
        }
        
        this.ready = true;
        return true;
      } catch (e) {
        console.error('❌ StorageManager 初始化失败，将降级使用 localStorage:', e);
        this.ready = false; // 标记未就绪，强制降级
        return false;
      }
    })();
    
    return this.initPromise;
  }

  // 保存数据（兼容 localStorage.setItem）
  async setItem(key, value) {
    const isReady = await this.init();
    
    if (!isReady) {
      try {
        localStorage.setItem(key, value);
        return true;
      } catch (e2) {
        console.error('localStorage 失败:', e2);
        return false;
      }
    }
    
    try {
      // 如果是图片数据，使用 saveImage
      if (typeof value === 'string' && value.startsWith('data:image')) {
        await IndexedDBManager.saveImage(key, value, 'image');
      } else {
        // 其他数据使用 saveData
        await IndexedDBManager.saveData(key, value);
      }
      return true;
    } catch (e) {
      console.error(`保存失败 ${key}:`, e);
      // 降级到 localStorage
      try {
        localStorage.setItem(key, value);
        return true;
      } catch (e2) {
        console.error('localStorage 也失败了:', e2);
        return false;
      }
    }
  }

  // 获取数据（兼容 localStorage.getItem）
  async getItem(key) {
    try {
      const isReady = await this.init();
      
      if (!isReady) {
        try { return localStorage.getItem(key); } catch(e) { return null; }
      }
      
      try {
        // 先尝试从 IndexedDB 获取
        let data = await IndexedDBManager.getData(key);
        
        // 如果没有，尝试从图片存储获取
        if (data === null) {
          data = await IndexedDBManager.getImage(key);
        }
        
        // 如果还是没有，尝试从 localStorage 获取（兼容性）
        if (data === null) {
          try { data = localStorage.getItem(key); } catch(e) { data = null; }
        }
        
        return data;
      } catch (e) {
        console.error(`读取失败 ${key}:`, e);
        // 降级到 localStorage
        try { return localStorage.getItem(key); } catch(e) { return null; }
      }
    } catch(e) {
      console.error(`获取流程失败 ${key}:`, e);
      try { return localStorage.getItem(key); } catch(e) { return null; }
    }
  }

  // 删除数据（兼容 localStorage.removeItem）
  async removeItem(key) {
    const isReady = await this.init();
    
    if (!isReady) {
      localStorage.removeItem(key);
      return true;
    }
    
    try {
      await IndexedDBManager.deleteData(key);
      await IndexedDBManager.deleteImage(key);
      localStorage.removeItem(key); // 同时清理 localStorage
      return true;
    } catch (e) {
      console.error(`删除失败 ${key}:`, e);
      localStorage.removeItem(key); // 降级清理
      return false;
    }
  }

  // 清空所有数据（兼容 localStorage.clear）
  async clear() {
    await this.init();
    
    try {
      // 清空 IndexedDB（需要重新实现）
      localStorage.clear();
      console.log('✅ 存储已清空');
      return true;
    } catch (e) {
      console.error('清空失败:', e);
      return false;
    }
  }

  // 获取存储使用情况
  async getStorageInfo() {
    await this.init();
    return await IndexedDBManager.getStorageInfo();
  }
}

// 创建全局实例
window.storage = new StorageManager();

// 提供同步版本的 API（使用缓存）
window.storageSync = {
  cache: {},
  
  setItem(key, value) {
    this.cache[key] = value;
    // 异步保存到 IndexedDB
    window.storage.setItem(key, value).catch(e => {
      console.error('异步保存失败:', e);
    });
  },
  
  getItem(key) {
    // 优先从缓存读取
    if (key in this.cache) {
      return this.cache[key];
    }
    // 降级到 localStorage
    return localStorage.getItem(key);
  },
  
  removeItem(key) {
    delete this.cache[key];
    window.storage.removeItem(key);
  }
};
