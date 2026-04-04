const html = `<div class="msg-menu"><div class="msg-menu-item" onclick="replyToMsg('"现在，我正在回复你。请问，你需要我回复什么具体内容？还是说，\\'持续回复\\'本身就是本次的测试项目？"',this)">回复</div></div>`;
const { JSDOM } = require('jsdom');
const dom = new JSDOM(html);
console.log(dom.window.document.body.innerHTML);
