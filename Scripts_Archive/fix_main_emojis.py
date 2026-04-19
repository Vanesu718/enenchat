import re

with open("js/main.js", "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    ("showToast('?? 图片大小超过1M，请选择更小的图片！');", "showToast('⚠️ 图片大小超过1M，请选择更小的图片！');"),
    ("showToast('?? 图标保存失败');", "showToast('❌ 图标保存失败');"),
    ("showToast('?? 存储空间不足！请清理数据或使用图片链接');", "showToast('⚠️ 存储空间不足！请清理数据或使用图片链接');"),
    ("showToast('?? 已自动清理旧数据');", "showToast('🧹 已自动清理旧数据');"),
    ("console.log('?? IndexedDB 存储空间:', storageInfo);", "console.log('📦 IndexedDB 存储空间:', storageInfo);"),
    ("alert('?? 文件大小超过1M，请选择更小的文件！');", "alert('⚠️ 文件大小超过1M，请选择更小的文件！');"),
    ("alert('?? 文档内容为空或无法解析！');", "alert('⚠️ 文档内容为空或无法解析！');"),
    ("alert('?? 不支持的文件格式！\\n\\n支持的格式：\\n? .txt（纯文本）\\n? .docx（Word 2007及以上版本）\\n\\n注意：不支持.doc（旧版Word）和.wps格式');", "alert('⚠️ 不支持的文件格式！\\n\\n支持的格式：\\n✅ .txt（纯文本）\\n✅ .docx（Word 2007及以上版本）\\n\\n注意：不支持.doc（旧版Word）和.wps格式');"),
    ("showToast('?? 文件大小超过1M，请选择更小的文件！');", "showToast('⚠️ 文件大小超过1M，请选择更小的文件！');"),
    ("showToast('?? 文档内容为空或无法解析！');", "showToast('⚠️ 文档内容为空或无法解析！');"),
    ("showToast('?? 不支持的文件格式！仅支持 .txt 和 .docx 格式');", "showToast('⚠️ 不支持的文件格式！仅支持 .txt 和 .docx 格式');"),
    ("showToast(isOfflineMode ? '已切换为线下模式 ??' : '已切换为线上模式 ??');", "showToast(isOfflineMode ? '已切换为线下模式 🌙' : '已切换为线上模式 ☀️');"),
    ("<div class=\"bc-label\">?? 心声</div>", "<div class=\"bc-label\">💭 心声</div>"),
    ("<div class=\"bc-label\">?? 地点</div>", "<div class=\"bc-label\">📍 地点</div>"),
    ("<div class=\"bc-label\">?? 心情</div>", "<div class=\"bc-label\">🎭 心情</div>"),
    ("<div class=\"bc-label\">?? 好感度</div>", "<div class=\"bc-label\">💖 好感度</div>"),
    ("<span>?? 情欲指数：</span>", "<span>🔥 情欲指数：</span>"),
    ("const reply = data.choices?.[0]?.message?.content || '来了来了！??';", "const reply = data.choices?.[0]?.message?.content || '来了来了！✨';"),
    ("【?? 核心指令 - 必须严格遵守】", "【⚠️ 核心指令 - 必须严格遵守】"),
    ("chatRecords[currentContactId].push({ side: 'right', content: '?? 我们还是分开吧...', time: Date.now() });", "chatRecords[currentContactId].push({ side: 'right', content: '💔 我们还是分开吧...', time: Date.now() });"),
    ("showToast('?? 正在告诉TA这个决定...', 3000);", "showToast('📢 正在告诉TA这个决定...', 3000);"),
    ("showToast('?? 已解除关系', 3000);", "showToast('💔 已解除关系', 3000);"),
    ("showToast('?? 正在精心准备求婚，等待TA的回应...', 3000);", "showToast('💍 正在精心准备求婚，等待TA的回应...', 3000);"),
    ("chatRecords[currentContactId].push({ side: 'right', content: '?? 我向你求婚了！', time: Date.now() });", "chatRecords[currentContactId].push({ side: 'right', content: '💍 我向你求婚了！', time: Date.now() });"),
    ("showToast('?? 求婚成功！你们结婚啦！', 4000);", "showToast('🎉 求婚成功！你们结婚啦！', 4000);"),
    ("showToast('?? AI正在回忆捕捉瞬间...');", "showToast('📸 AI正在回忆捕捉瞬间...');"),
    ("alert('?? 图片大小超过2M，请选择更小的图片！');", "alert('⚠️ 图片大小超过2M，请选择更小的图片！');"),
    ("showToast('?? 背景图保存失败，存储空间不足！');", "showToast('⚠️ 背景图保存失败，存储空间不足！');"),
    ("alert('?? 部分数据可能未完全清空，请手动清除浏览器缓存。');", "alert('⚠️ 部分数据可能未完全清空，请手动清除浏览器缓存。');"),
    ("if (!confirm('?? 导入备份将覆盖当前所有数据，确定继续吗？')) {", "if (!confirm('⚠️ 导入备份将覆盖当前所有数据，确定继续吗？')) {"),
    ("// ?? 兼容性处理：如果没有version字段，说明是旧版本备份", "// 💡 兼容性处理：如果没有version字段，说明是旧版本备份"),
    ("if (!confirm(`确定要删除联系人\"${contact.name}\"吗？\\n\\n?? 这将同时删除与TA的所有聊天记录、设置和状态信息，且无法恢复！`)) {", "if (!confirm(`确定要删除联系人\"${contact.name}\"吗？\\n\\n⚠️ 这将同时删除与TA的所有聊天记录、设置和状态信息，且无法恢复！`)) {"),
    ("console.log('?? 存储空间使用情况:', storageInfo);", "console.log('📦 存储空间使用情况:', storageInfo);"),
    ("console.warn('?? 存储管理器降级为 localStorage');", "console.warn('⚠️ 存储管理器降级为 localStorage');"),
    ("{ key: 'gossip', emoji: '???', name: '风声暗巷', desc: '八卦版' },", "{ key: 'gossip', emoji: '🗣️', name: '风声暗巷', desc: '八卦版' },"),
    ("{ key: 'entertainment', emoji: '??', name: '星海瞭望台', desc: '娱乐版' },", "{ key: 'entertainment', emoji: '🌟', name: '星海瞭望台', desc: '娱乐版' },"),
    ("{ key: 'horror', emoji: '??', name: '夜谈档案馆', desc: '恐怖版' }", "{ key: 'horror', emoji: '👻', name: '夜谈档案馆', desc: '恐怖版' }"),
    ("<div style=\"font-size:14px; font-weight:500; color:var(--text-dark);\">${board.emoji || '??'} ${board.name}</div>", "<div style=\"font-size:14px; font-weight:500; color:var(--text-dark);\">${board.emoji || '📌'} ${board.name}</div>"),
    ("const emojis = ['??', '??', '??', '??', '??', '??', '??', '??'];", "const emojis = ['🌟','🌈','🎈','🎉','🎨','✨','🔮','🎭'];"),
    ("name: '风声暗巷',\n    emoji: '???',", "name: '风声暗巷',\n    emoji: '🗣️',"),
    ("name: '星海瞭望台',\n    emoji: '??',", "name: '星海瞭望台',\n    emoji: '🌟',"),
    ("name: '夜谈档案馆',\n    emoji: '??',", "name: '夜谈档案馆',\n    emoji: '👻',"),
    ("<span>??</span> 已有${post.comments?.length || 0}条热议", "<span>🔥</span> 已有${post.comments?.length || 0}条热议"),
    ("const reply = data.choices?.[0]?.message?.content || '??';", "const reply = data.choices?.[0]?.message?.content || '✨';"),
    ("showToast('?? 请先在设置中配置AI');", "showToast('⚠️ 请先在设置中配置AI');"),
    ("showToast('? ??: ' + e.message);", "showToast('❌ 错误: ' + e.message);"),
    ("// rulesEl.innerHTML = `<span style=\"color:${board.rulesColor}; font-weight:600;\">?? 发帖须知：</span><span style=\"color:${board.rulesTextColor};\">${board.rules}</span>`;", "// rulesEl.innerHTML = `<span style=\"color:${board.rulesColor}; font-weight:600;\">📌 发帖须知：</span><span style=\"color:${board.rulesTextColor};\">${board.rules}</span>`;"),
    ("alert('?? 本地上传一次只能上传1张图片！如果需要多张请使用链接上传。');", "alert('⚠️ 本地上传一次只能上传1张图片！如果需要多张请使用链接上传。');"),
    ("alert('?? 图片大小超过2M，请选择更小的图片！');", "alert('⚠️ 图片大小超过2M，请选择更小的图片！');"),
    ("alert('?? 最多只能上传4张图片！');", "alert('⚠️ 最多只能上传4张图片！');"),
    ("showToast('?? 朋友圈保存失败');", "showToast('❌ 朋友圈保存失败');"),
    ("alert('?? 图片大小超过1M，请选择更小的图片！');", "alert('⚠️ 图片大小超过1M，请选择更小的图片！');"),
    ("alert('?? 封面图保存失败，存储空间不足！建议使用更小的图片或清理数据。');", "alert('⚠️ 封面图保存失败，存储空间不足！建议使用更小的图片或清理数据。');"),
    ("// ?? 改为“串行”生成，避免并发请求触发 403 错误", "// 💡 改为“串行”生成，避免并发请求触发 403 错误"),
    ("loadingEl.innerText = '?? 正在生成记忆总结...';", "loadingEl.innerText = '🧠 正在生成记忆总结...';"),
    ("display:${isStmBatchDeleteMode?'none':'block'};\">?? 编辑</div>", "display:${isStmBatchDeleteMode?'none':'block'};\">✏️ 编辑</div>"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open("js/main.js", "w", encoding="utf-8") as f:
    f.write(content)
