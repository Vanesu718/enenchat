#!/bin/sh

# Make a backup
cp js/main.js js/main.js.bak

# Use sed to replace ? with emojis
sed -i 's/?? 图片大小超过/❌ 图片大小超过/g' js/main.js
sed -i 's/?? 图标保存失败/❌ 图标保存失败/g' js/main.js
sed -i 's/?? 存储空间不足/❌ 存储空间不足/g' js/main.js
sed -i 's/?? 已自动清理旧数据/🧹 已自动清理旧数据/g' js/main.js
sed -i 's/?? IndexedDB 存储空间/📦 IndexedDB 存储空间/g' js/main.js
sed -i 's/?? 文件大小超过/❌ 文件大小超过/g' js/main.js
sed -i 's/?? 文档内容为空或无法解析/❌ 文档内容为空或无法解析/g' js/main.js
sed -i 's/?? 不支持的文件格式/❌ 不支持的文件格式/g' js/main.js
sed -i 's/已切换为线下模式 ??/已切换为线下模式 📴/g' js/main.js
sed -i 's/已切换为线上模式 ??/已切换为线上模式 🌐/g' js/main.js
sed -i 's/?? 心声/💭 心声/g' js/main.js
sed -i 's/?? 地点/📍 地点/g' js/main.js
sed -i 's/?? 心情/🎭 心情/g' js/main.js
sed -i 's/?? 好感度/❤️ 好感度/g' js/main.js
sed -i 's/?? 情欲指数/🔥 情欲指数/g' js/main.js
sed -i 's/来了来了！??/来了来了！🏃/g' js/main.js
sed -i 's/?? 我们还是分开吧/💔 我们还是分开吧/g' js/main.js
sed -i 's/?? 正在告诉TA这个决定/⏳ 正在告诉TA这个决定/g' js/main.js
sed -i 's/?? 已解除关系/💔 已解除关系/g' js/main.js
sed -i 's/?? 正在精心准备求婚/💍 正在精心准备求婚/g' js/main.js
sed -i 's/?? 我向你求婚了！/💍 我向你求婚了！/g' js/main.js
sed -i 's/?? 求婚成功！/🎉 求婚成功！/g' js/main.js
sed -i 's/?? AI正在回忆捕捉瞬间/🧠 AI正在回忆捕捉瞬间/g' js/main.js
sed -i 's/?? 背景图保存失败/❌ 背景图保存失败/g' js/main.js
sed -i 's/?? 部分数据可能未完全清空/⚠️ 部分数据可能未完全清空/g' js/main.js
sed -i 's/?? 导入备份将覆盖/⚠️ 导入备份将覆盖/g' js/main.js
sed -i 's/?? 兼容性处理/🔧 兼容性处理/g' js/main.js
sed -i 's/?? 这将同时删除与TA的所有聊天记录/⚠️ 这将同时删除与TA的所有聊天记录/g' js/main.js
sed -i 's/?? 存储空间使用情况/📦 存储空间使用情况/g' js/main.js
sed -i 's/?? 存储管理器降级/⚠️ 存储管理器降级/g' js/main.js
sed -i 's/??? 风声暗巷/🗣️ 风声暗巷/g' js/main.js
sed -i 's/?? 星海瞭望台/🌟 星海瞭望台/g' js/main.js
sed -i 's/?? 夜谈档案馆/👻 夜谈档案馆/g' js/main.js
sed -i 's/?? 已有/🔥 已有/g' js/main.js
sed -i 's/?? 点赞/👍 点赞/g' js/main.js
sed -i 's/?? 评论/💬 评论/g' js/main.js
sed -i 's/content || '\'\?\?\''/content || '\'🤔\''/g' js/main.js
sed -i 's/?? 请先在设置中配置AI/⚠️ 请先在设置中配置AI/g' js/main.js
sed -i 's/??: /❌: /g' js/main.js
sed -i 's/?? 发帖须知/📝 发帖须知/g' js/main.js
sed -i 's/?? 本地上传一次只能上传/❌ 本地上传一次只能上传/g' js/main.js
sed -i 's/?? 最多只能上传/❌ 最多只能上传/g' js/main.js
sed -i 's/?? 朋友圈保存失败/❌ 朋友圈保存失败/g' js/main.js
sed -i 's/?? 封面图保存失败/❌ 封面图保存失败/g' js/main.js
sed -i 's/?? 改为“串行”生成/🔧 改为“串行”生成/g' js/main.js
sed -i 's/?? 已赞/❤️ 已赞/g' js/main.js
sed -i 's/?? 赞/🤍 赞/g' js/main.js
sed -i 's/??? 删除/🗑️ 删除/g' js/main.js
sed -i 's/?? 正在生成记忆总结/⏳ 正在生成记忆总结/g' js/main.js
sed -i 's/?? 编辑/✏️ 编辑/g' js/main.js

sed -i 's/? 默认/👥 默认/g' js/main.js
sed -i 's/? 主题已应用/🎨 主题已应用/g' js/main.js
sed -i 's/? 图标${index}已保存到 IndexedDB/✅ 图标${index}已保存到 IndexedDB/g' js/main.js
sed -i 's/? 清理后保存成功/✅ 清理后保存成功/g' js/main.js
sed -i 's/? 存储空间严重不足/❌ 存储空间严重不足/g' js/main.js
sed -i 's/? 图片已保存到 IndexedDB/✅ 图片已保存到 IndexedDB/g' js/main.js
sed -i 's/? 图片已保存/✅ 图片已保存/g' js/main.js
sed -i 's/? 分组已添加/✅ 分组已添加/g' js/main.js
sed -i 's/? 分组已删除/✅ 分组已删除/g' js/main.js
sed -i 's/? 文档内容已成功导入/✅ 文档内容已成功导入/g' js/main.js
sed -i 's/? 文件读取失败/❌ 文件读取失败/g' js/main.js
sed -i 's/? Word文档解析库未加载/❌ Word文档解析库未加载/g' js/main.js
sed -i 's/? Word文档解析失败/❌ Word文档解析失败/g' js/main.js
sed -i 's/? Word文档内容已成功导入/✅ Word文档内容已成功导入/g' js/main.js
sed -i 's/? 群聊已创建/✅ 群聊已创建/g' js/main.js
sed -i 's/? 保存失败/❌ 保存失败/g' js/main.js
sed -i 's/? 联系人已永久保存/✅ 联系人已永久保存/g' js/main.js
sed -i 's/? 保存为当前联系人独立的模式设置/🔧 保存为当前联系人独立的模式设置/g' js/main.js
sed -i 's/? 同步背景到其他三个页面/🔧 同步背景到其他三个页面/g' js/main.js
sed -i 's/? 使用 IndexedDB 保存背景图/🔧 使用 IndexedDB 保存背景图/g' js/main.js
sed -i 's/? 背景图已保存/✅ 背景图已保存/g' js/main.js
sed -i 's/? 正在打包聊天数据/📦 正在打包聊天数据/g' js/main.js
sed -i 's/? 正在打包全局数据/📦 正在打包全局数据/g' js/main.js
sed -i 's/? 聊天备份已导出/✅ 聊天备份已导出/g' js/main.js
sed -i 's/? 全局备份已导出/✅ 全局备份已导出/g' js/main.js
sed -i 's/? 所有数据已清空/✅ 所有数据已清空/g' js/main.js
sed -i 's/? 备份文件格式不正确/❌ 备份文件格式不正确/g' js/main.js
sed -i 's/? 备份已成功导入/✅ 备份已成功导入/g' js/main.js
sed -i 's/? 导入失败/❌ 导入失败/g' js/main.js
sed -i 's/? 联系人已删除/✅ 联系人已删除/g' js/main.js
sed -i 's/? 叙事美化设置已保存/✅ 叙事美化设置已保存/g' js/main.js
sed -i 's/? 存储管理器初始化成功/✅ 存储管理器初始化成功/g' js/main.js
sed -i 's/? 存储管理器初始化异常/❌ 存储管理器初始化异常/g' js/main.js
sed -i 's/? 从 IndexedDB 加载图片/🔧 从 IndexedDB 加载图片/g' js/main.js
sed -i 's/? 页面加载时同步背景到所有页面/🔧 页面加载时同步背景到所有页面/g' js/main.js
sed -i 's/? 初始化过程中发生错误/❌ 初始化过程中发生错误/g' js/main.js
sed -i 's/? AI 正在构思版块介绍/🧠 AI 正在构思版块介绍/g' js/main.js
sed -i 's/? AI 生成完成/✅ AI 生成完成/g' js/main.js
sed -i 's/? 生成失败/❌ 生成失败/g' js/main.js
sed -i 's/? 版块已创建/✅ 版块已创建/g' js/main.js
sed -i 's/? 版块已删除/✅ 版块已删除/g' js/main.js
sed -i 's/? 预设版块已隐藏/✅ 预设版块已隐藏/g' js/main.js
sed -i 's/? 预设版块已恢复/✅ 预设版块已恢复/g' js/main.js
sed -i 's/? 评论已发布/✅ 评论已发布/g' js/main.js
sed -i 's/? AI正在生成新帖子/🧠 AI正在生成新帖子/g' js/main.js
sed -i 's/? 刷新成功，正在生成现场讨论/✅ 刷新成功，正在生成现场讨论/g' js/main.js
sed -i 's/? 正在通过模块A优化内容/🧠 正在通过模块A优化内容/g' js/main.js
sed -i 's/? 发帖成功/✅ 发帖成功/g' js/main.js
sed -i 's/? 已删除/🗑️ 已删除/g' js/main.js
sed -i 's/? 请求失败/❌ 请求失败/g' js/main.js
sed -i 's/? 求婚失败/❌ 求婚失败/g' js/main.js
sed -i 's/? 瞬间已记录/✅ 瞬间已记录/g' js/main.js
sed -i 's/? 回忆失败/❌ 回忆失败/g' js/main.js
sed -i 's/? 已应用用户面具/✅ 已应用用户面具/g' js/main.js
sed -i 's/? 所有聊天设置已保存/✅ 所有聊天设置已保存/g' js/main.js
sed -i 's/? 聊天记录及记忆已清空/✅ 聊天记录及记忆已清空/g' js/main.js
sed -i 's/? 预设已保存/✅ 预设已保存/g' js/main.js
sed -i 's/? 保存预设失败/❌ 保存预设失败/g' js/main.js
sed -i 's/? 预设已删除/✅ 预设已删除/g' js/main.js
sed -i 's/? 删除预设失败/❌ 删除预设失败/g' js/main.js
sed -i 's/? 修复后的拉取模型函数/🔧 修复后的拉取模型函数/g' js/main.js
sed -i 's/? 用户面具已保存/✅ 用户面具已保存/g' js/main.js
sed -i 's/? 世界书条目已永久保存/✅ 世界书条目已永久保存/g' js/main.js
sed -i 's/? 好感度已清零/✅ 好感度已清零/g' js/main.js
sed -i 's/? 甜蜜设置已保存/✅ 甜蜜设置已保存/g' js/main.js
sed -i 's/? 页面初始化时重新应用主题类/🔧 页面初始化时重新应用主题类/g' js/main.js
sed -i 's/? 如果当前主题是线下简约/🔧 如果当前主题是线下简约/g' js/main.js

echo "Replacement completed."
