const fs = require('fs');

try {
    let mainJs = fs.readFileSync('js/main.js', 'utf8');
    // 查找并替换 msg-menu-item 里的所有乱码，强制改为 "回复"
    let replaced = mainJs.replace(/(<div class="msg-menu-item" onclick="replyToMsg\([^>]+\)[^>]*>)[^<]+(<\/div>)/g, '$1回复$2');
    
    // 如果没有找到，直接用包含乱码的正则匹配（以防上面正则没生效）
    // 之前看到类似 data-reply-text="${replyText}">ظ</div>
    replaced = replaced.replace(/data-reply-text="\$\{replyText\}">[^<]+<\/div>/g, 'data-reply-text="${replyText}">回复</div>');
    
    fs.writeFileSync('js/main.js', replaced, 'utf8');
    console.log("Fixed js/main.js");
} catch(e) {
    console.error("Error in main.js fix:", e);
}

try {
    let chatCss = fs.readFileSync('css/chat.css', 'utf8');
    // 添加防误触和屏蔽移动端 hover 的代码
    if (!chatCss.includes('/* 移动端防误触 */')) {
        chatCss += `
/* 移动端防误触 */
@media (hover: none) and (pointer: coarse) {
  .msg-menu {
    display: none !important;
  }
  .msg-row {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
  }
  .msg-content {
    -webkit-tap-highlight-color: transparent;
    -webkit-touch-callout: none;
  }
}
`;
        fs.writeFileSync('css/chat.css', chatCss, 'utf8');
        console.log("Fixed css/chat.css");
    }
} catch(e) {
    console.error("Error in chat.css fix:", e);
}
