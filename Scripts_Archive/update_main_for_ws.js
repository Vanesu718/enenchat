// 1. Init writingStyles data
const initCode = `      const rawWritingStyles = await getFromStorage('WRITING_STYLES');
      try {
        writingStyles = rawWritingStyles ? (typeof rawWritingStyles === 'string' ? JSON.parse(rawWritingStyles) : rawWritingStyles) : [];
        if (!Array.isArray(writingStyles)) writingStyles = [];
      } catch(e) { console.error('解析文风失败', e); writingStyles = []; }
`;

// 2. Add writing style functions
const wsFunctions = `
  // ================= 文风管理逻辑 =================
  let currentWsFilter = 'all';

  function filterWritingStyle(cat) {
    currentWsFilter = cat;
    document.querySelectorAll('.ws-tab').forEach(el => {
      el.classList.remove('active');
      el.style.background = '#f5f5f5';
      el.style.color = 'var(--text-dark)';
    });
    const activeTab = document.querySelector(\`.ws-tab[data-category="\${cat}"]\`);
    if (activeTab) {
      activeTab.classList.add('active');
      activeTab.style.background = 'var(--main-pink)';
      activeTab.style.color = 'white';
    }
    renderWritingStyleList();
  }

  function renderWritingStyleList() {
    const el = document.getElementById('writingStyleList');
    if (!el) return;
    
    let filteredEntries = writingStyles;
    if (currentWsFilter !== 'all') {
      filteredEntries = writingStyles.filter(e => e.category === currentWsFilter);
    }
    
    if (filteredEntries.length === 0) {
      el.innerHTML = '<div class="empty-tip">暂无文风条目<br>点击右上角 + 添加</div>';
      return;
    }
    
    el.innerHTML = '';
    filteredEntries.forEach((entry) => {
      const idx = writingStyles.indexOf(entry);
      const div = document.createElement('div');
      div.className = 'contact-item';
      div.style.position = 'relative';
      
      let triggerTag = '';
      if (entry.triggerType === 'keyword') {
        triggerTag = \`<span style="background:#e8f4f8; color:#0088cc; padding:2px 6px; border-radius:4px; font-size:10px; margin-left:5px;">关键词触发</span>\`;
      } else {
        triggerTag = \`<span style="background:#f0e8df; color:#8c6d46; padding:2px 6px; border-radius:4px; font-size:10px; margin-left:5px;">常驻触发</span>\`;
      }
      
      div.innerHTML = \`
        <div style="flex:1;">
          <div style="font-size:14px; font-weight:bold; color:var(--text-dark); margin-bottom:4px; display:flex; align-items:center;">
            \${escapeHTML(entry.name)} 
            <span style="font-size:10px; background:#f0f0f0; padding:2px 6px; border-radius:4px; margin-left:5px; color:#666;">\${escapeHTML(entry.category || '未分类')}</span>
            \${triggerTag}
          </div>
          <div style="font-size:12px; color:var(--text-light); display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; text-overflow:ellipsis; line-height:1.4;">
            \${escapeHTML(entry.content || '')}
          </div>
        </div>
        <div style="display:flex; gap:8px;">
          <button class="btn-primary" style="padding:4px 8px; font-size:12px;" onclick="editWritingStyleEntry(\${idx})">编辑</button>
          <button class="btn-primary" style="padding:4px 8px; font-size:12px; background:#f44336;" onclick="deleteWritingStyleEntry(\${idx})">删除</button>
        </div>
      \`;
      el.appendChild(div);
    });
  }

  async function saveWritingStyleEntry() {
    const name = document.getElementById('wsEntryName').value.trim();
    const keywords = document.getElementById('wsEntryKeywords').value.trim();
    const content = document.getElementById('wsEntryContent').value.trim();
    const category = document.getElementById('wsEntryCategory').value;
    const triggerType = document.querySelector('input[name="wsTriggerType"]:checked').value;
    
    if (!name || !content) {
      alert('名称和内容不能为空！');
      return;
    }
    
    if (triggerType === 'keyword' && !keywords) {
      alert('关键词触发模式下，触发词不能为空！');
      return;
    }

    const compressedContent = await compressWritingStyleWithAI(content);
    if (!compressedContent) {
        return; // 用户取消或压缩失败
    }
    
    if (window._isEditingWs && window._editingWsId) {
      const idx = writingStyles.findIndex(e => e.id === window._editingWsId);
      if (idx > -1) {
        writingStyles[idx] = {
          ...writingStyles[idx],
          name,
          keywords,
          content: compressedContent,
          originalContent: content,
          category,
          triggerType,
          updateTime: Date.now()
        };
      } else {
        writingStyles.push({ 
          id: window._editingWsId, 
          name, 
          keywords, 
          content: compressedContent,
          originalContent: content,
          category,
          triggerType,
          createTime: Date.now()
        });
      }
    } else {
      writingStyles.push({ 
        id: Date.now().toString(), 
        name, 
        keywords, 
        content: compressedContent,
        originalContent: content,
        category,
        triggerType,
        createTime: Date.now()
      });
    }
    
    await saveToStorage('WRITING_STYLES', JSON.stringify(writingStyles));
    
    document.getElementById('wsEntryName').value = '';
    document.getElementById('wsEntryKeywords').value = '';
    document.getElementById('wsEntryContent').value = '';
    
    window._isEditingWs = false;
    window._editingWsId = null;
    
    closeSub('add-writing-style');
    renderWritingStyleList();
  }

  async function compressWritingStyleWithAI(originalContent) {
      if(originalContent.length <= 200) {
          return originalContent;
      }
      if (!apiKeys || !apiKeys.sk) {
          alert("请先配置API Key后再使用智能文风压缩！");
          return null;
      }
      const isConfirm = confirm(\`当前文风内容(\${originalContent.length}字)较长，系统将调用AI压缩至200字以内（将消耗少量Token）。是否继续？\n压缩后的内容将用于实际注入，原内容将作为备份保存。\`);
      if(!isConfirm) return null;

      const btn = document.querySelector('#add-writing-style .page-header button');
      if(btn) {
          btn.innerText = "压缩中...";
          btn.disabled = true;
      }

      try {
          const prompt = \`请将以下文本压缩到200字以内，提取其核心的文风、语气、口癖、句式特征和用词习惯。尽量保留代表性的特征和关键规则。\n\n待压缩文本：\n\${originalContent}\`;

          const response = await callAIWithRetry(prompt, "你是一个专业的文本压缩与文风特征提取助手。");
          if(response) {
             if(btn) {
                 btn.innerText = "保存";
                 btn.disabled = false;
             }
             alert("文风特征提取完成并已保存！");
             return response;
          } else {
              if(btn) {
                  btn.innerText = "保存";
                  btn.disabled = false;
              }
              alert("AI压缩提炼失败，请检查API配置或稍后重试！");
              return null;
          }
      } catch(e) {
          console.error("文风提炼失败:", e);
           if(btn) {
               btn.innerText = "保存";
               btn.disabled = false;
           }
           alert("AI压缩提炼发生异常，请查看控制台！");
           return null;
      }
  }

  function editWritingStyleEntry(idx) {
    const entry = writingStyles[idx];
    window._isEditingWs = true;
    window._editingWsId = entry.id;
    
    document.getElementById('wsEntryName').value = entry.name;
    document.getElementById('wsEntryKeywords').value = entry.keywords || '';
    document.getElementById('wsEntryContent').value = entry.originalContent || entry.content;
    document.getElementById('wsEntryCategory').value = entry.category || '默认';
    
    if (entry.triggerType === 'keyword') {
      document.querySelector('input[name="wsTriggerType"][value="keyword"]').checked = true;
      document.getElementById('wsKeywordDiv').style.display = 'block';
    } else {
      document.querySelector('input[name="wsTriggerType"][value="always"]').checked = true;
      document.getElementById('wsKeywordDiv').style.display = 'none';
    }
    
    openSub('add-writing-style');
  }

  async function deleteWritingStyleEntry(idx) {
    if (!confirm('确定删除这个文风条目吗？')) return;
    writingStyles.splice(idx, 1);
    await saveToStorage('WRITING_STYLES', JSON.stringify(writingStyles));
    renderWritingStyleList();
    alert('已删除！');
  }

`;

const fs = require('fs');
let content = fs.readFileSync('js/main.js', 'utf-8');

if (content.indexOf('let writingStyles = [];') !== -1 && content.indexOf("const rawWritingStyles = await getFromStorage('WRITING_STYLES');") === -1) {
    content = content.replace("const rawWbEntries = await getFromStorage('WORLDBOOK_ENTRIES');", initCode + "      const rawWbEntries = await getFromStorage('WORLDBOOK_ENTRIES');");
}

if (content.indexOf('function renderWritingStyleList()') === -1) {
    content = content.replace('function renderWorldBookList() {', wsFunctions + "function renderWorldBookList() {");
}

fs.writeFileSync('js/main.js', content, 'utf-8');
console.log('done');