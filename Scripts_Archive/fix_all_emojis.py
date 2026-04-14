import re

def get_emoji(text):
    if any(x in text for x in ["失败", "不正确", "错误", "不是有效", "严重不足", "异常"]):
        return "❌"
    if any(x in text for x in ["不足", "超过", "为空", "不支持", "未加载", "格式不正确", "必须", "警告", "请先"]):
        return "⚠️"
    if any(x in text for x in ["AI", "智能", "提炼", "构思", "提取", "回忆"]):
        return "✨"
    if any(x in text for x in ["正在", "请稍候", "稍等", "打包"]):
        return "⏳"
    if any(x in text for x in ["删除", "清空", "清零", "解除"]):
        return "🗑️"
    if any(x in text for x in ["求婚", "结婚"]):
        return "💍"
    if any(x in text for x in ["成功", "已应用", "已保存", "已添加", "已导入", "已创建", "完成", "已导出", "已记录", "已恢复", "已发布", "发布成功", "已隐藏", "已应用"]):
        return "✅"
    if any(x in text for x in ["图片", "背景图", "封面图"]):
        return "🖼️"
    if any(x in text for x in ["存储", "容量", "空间"]):
        return "📦"
    return "✅"  # default fallback

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        def replacer(match):
            prefix = match.group(1)
            # look ahead up to 20 chars to determine context
            ahead = match.string[match.end():match.end()+20]
            emoji = get_emoji(ahead)
            return f"{prefix}{emoji} "

        # Match single or double question marks after a quote (with optional spaces)
        new_content = re.sub(r"(['`\"])\s*(?:\?\?|\?)\s+", replacer, content)
        
        # HTML tag content matching
        def html_replacer(match):
            prefix = match.group(1)
            text = match.group(2)
            emoji = get_emoji(text)
            return f"{prefix}{emoji} {text}"
            
        new_content = re.sub(r"(>)\s*(?:\?\?|\?)\s+([^<]+)", html_replacer, new_content)
        
        # Manual replacements for specific known cases
        new_content = new_content.replace("// ?? ", "// ⚠️ ")
        new_content = new_content.replace("// ? ", "// ⚠️ ")
        new_content = new_content.replace("?? 情欲指数", "🔥 情欲指数")
        new_content = new_content.replace("?? 这将同时删除", "⚠️ 这将同时删除")
        new_content = new_content.replace("'???'", "'📰'")
        new_content = new_content.replace("'??', name: '星海瞭望台'", "'🌟', name: '星海瞭望台'")
        new_content = new_content.replace("'??', name: '夜谈档案馆'", "'👻', name: '夜谈档案馆'")
        new_content = new_content.replace("['??', '??', '??', '??', '??', '??', '??', '??']", "['😀', '😂', '🥰', '😎', '🤔', '😭', '😡', '😴']")
        new_content = new_content.replace("emoji: '???'", "emoji: '📰'")
        new_content = new_content.replace("emoji: '??'", "emoji: '🌟'")
        new_content = new_content.replace("<span>??</span>", "<span>🔥</span>")
        new_content = new_content.replace("?? 发帖须知", "📢 发帖须知")
        new_content = new_content.replace("来了来了！??", "来了来了！🏃")
        new_content = new_content.replace("我们还是分开吧...??", "我们还是分开吧...💔")
        new_content = new_content.replace("?? 我们还是分开吧", "💔 我们还是分开吧")
        new_content = new_content.replace("? ??: ", "❌ 错误: ")
        new_content = new_content.replace("?? 编辑", "✏️ 编辑")
        new_content = new_content.replace("? Word文档", "📄 Word文档")
        new_content = new_content.replace("\\n? .txt", "\\n📄 .txt")
        new_content = new_content.replace("\\n? .docx", "\\n📄 .docx")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        print(f"Processed {filepath}")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

process_file('js/main.js')
process_file('index.html')
print("Done!")
