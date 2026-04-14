import os
import re

INDEX_FILE = 'index.html'
MAIN_JS = 'js/main.js'
CHAT_CSS = 'css/chat.css'

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("Reading index.html...")
    index_html = read_file(INDEX_FILE)

    # Inject Modals into index.html
    modals_html = """
    <!-- Red Packet Send Modal -->
    <div id="redPacketSendModal" class="modal" style="display:none;">
      <div class="modal-content red-packet-modal">
        <div class="modal-header">
          <h3>发红包</h3>
          <button class="close-btn" onclick="document.getElementById('redPacketSendModal').style.display='none'">×</button>
        </div>
        <div class="modal-body">
          <div class="rp-input-group">
            <label>金额</label>
            <input type="number" id="rpAmount" placeholder="0.00" step="0.01">
            <span>元</span>
          </div>
          <div class="rp-input-group">
            <label>留言</label>
            <input type="text" id="rpGreeting" value="恭喜发财，大吉大利">
          </div>
          <div class="rp-cover-section">
            <label>红包封面 (3:4)</label>
            <div class="rp-cover-preview" id="rpCoverPreview" style="background-image: url('ICON/红包.png');">
              <button class="btn btn-primary" onclick="document.getElementById('rpCoverInput').click()">上传封面</button>
            </div>
            <input type="file" id="rpCoverInput" accept="image/*" style="display:none;" onchange="handleRpCover(this)">
            <div id="rpCoverHistory" class="rp-cover-history"></div>
          </div>
          <div class="rp-amount-display">
            ￥<span id="rpAmountDisplay">0.00</span>
          </div>
          <button class="btn rp-send-btn" onclick="sendRedPacket()">塞钱进红包</button>
        </div>
      </div>
    </div>

    <!-- Red Packet Open Modal -->
    <div id="redPacketOpenModal" class="modal rp-open-modal-container" style="display:none;">
      <div class="rp-open-content" id="rpOpenContent">
        <button class="close-btn rp-close-btn" onclick="document.getElementById('redPacketOpenModal').style.display='none'">×</button>
        <div class="rp-open-avatar">
          <img id="rpOpenAvatar" src="ICON/黑猫.png">
        </div>
        <div class="rp-open-name" id="rpOpenName">User</div>
        <div class="rp-open-greeting" id="rpOpenGreeting">恭喜发财，大吉大利</div>
        <div class="rp-open-amount" id="rpOpenAmountBox" style="display:none;">
          <span id="rpOpenAmount">0.00</span><span style="font-size: 0.5em;">元</span>
        </div>
        <div class="rp-open-button" id="rpOpenBtn" onclick="openRedPacket()">拆</div>
      </div>
    </div>

    <!-- Transfer Send Modal -->
    <div id="transferSendModal" class="modal" style="display:none;">
      <div class="modal-content transfer-modal">
        <div class="modal-header">
          <h3>转账</h3>
          <button class="close-btn" onclick="document.getElementById('transferSendModal').style.display='none'">×</button>
        </div>
        <div class="modal-body">
          <div class="tf-amount-section">
            <div>转账金额</div>
            <div class="tf-input-wrapper">
              <span>￥</span>
              <input type="number" id="tfAmount" placeholder="0.00" step="0.01">
            </div>
          </div>
          <div class="tf-remark-section">
            <input type="text" id="tfRemark" placeholder="添加转账说明" value="转账">
          </div>
          <button class="btn tf-send-btn" onclick="sendTransfer()">转账</button>
        </div>
      </div>
    </div>

    <!-- Transfer Open Modal -->
    <div id="transferOpenModal" class="modal" style="display:none;">
      <div class="modal-content tf-open-modal">
        <div class="modal-header tf-open-header">
          <button class="close-btn" onclick="document.getElementById('transferOpenModal').style.display='none'">×</button>
        </div>
        <div class="tf-open-icon"><img src="ICON/转账.png"></div>
        <div class="tf-open-status" id="tfOpenStatus">待收款</div>
        <div class="tf-open-amount">￥<span id="tfOpenAmount">0.00</span></div>
        <div class="tf-open-remark" id="tfOpenRemark">转账</div>
        <div class="tf-open-action" id="tfOpenAction" onclick="acceptTransfer()">确认收款</div>
      </div>
    </div>
    """

    if "redPacketSendModal" not in index_html:
        index_html = index_html.replace("</body>", modals_html + "\n</body>")
        write_file(INDEX_FILE, index_html)
        print("Modals injected into index.html")
    
    print("Reading chat.css...")
    chat_css = read_file(CHAT_CSS)
    css_additions = """
/* Red Packet & Transfer Modals */
.red-packet-modal {
  background: #f1f1f1;
}
.rp-input-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}
.rp-input-group input {
  border: none;
  text-align: right;
  font-size: 16px;
  flex: 1;
  margin: 0 10px;
  outline: none;
}
.rp-cover-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}
.rp-cover-preview {
  width: 120px;
  height: 160px;
  background-size: cover;
  background-position: center;
  border-radius: 8px;
  margin: 10px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 1px solid #ddd;
}
.rp-cover-history {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 5px 0;
}
.rp-cover-history img {
  width: 60px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid transparent;
}
.rp-cover-history img.selected {
  border-color: #ea5a5a;
}
.rp-amount-display {
  text-align: center;
  font-size: 32px;
  font-weight: bold;
  margin: 20px 0;
}
.rp-send-btn {
  background: #ea5a5a;
  color: white;
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  border: none;
}

.rp-open-modal-container {
  display: flex;
  align-items: center;
  justify-content: center;
}
.rp-open-content {
  width: 300px;
  height: 400px;
  background: #d84e43;
  border-radius: 12px;
  position: relative;
  text-align: center;
  color: #fae3b7;
  background-size: cover;
  background-position: center;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.rp-open-content::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(216, 78, 67, 0.85);
  border-radius: 12px;
  z-index: 0;
}
.rp-open-content.has-custom-cover::before {
  background: rgba(0, 0, 0, 0.4);
}
.rp-open-content > * {
  position: relative;
  z-index: 1;
}
.rp-close-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  color: rgba(255,255,255,0.7);
  font-size: 24px;
  background: none;
  border: none;
}
.rp-open-avatar img {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  margin-top: 30px;
}
.rp-open-name {
  font-size: 16px;
  margin-top: 10px;
}
.rp-open-greeting {
  font-size: 20px;
  margin-top: 20px;
}
.rp-open-amount {
  font-size: 40px;
  font-weight: bold;
  margin-top: 30px;
  color: #fae3b7;
}
.rp-open-button {
  width: 80px;
  height: 80px;
  background: #ebd29f;
  color: #333;
  border-radius: 50%;
  line-height: 80px;
  font-size: 32px;
  font-weight: bold;
  margin: 40px auto 0;
  cursor: pointer;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.transfer-modal {
  background: #f1f1f1;
}
.tf-amount-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
}
.tf-input-wrapper {
  display: flex;
  align-items: center;
  font-size: 30px;
  margin-top: 10px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}
.tf-input-wrapper input {
  border: none;
  font-size: 36px;
  width: 100%;
  outline: none;
  margin-left: 10px;
}
.tf-remark-section {
  margin-bottom: 20px;
}
.tf-remark-section input {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  outline: none;
}
.tf-send-btn {
  background: #1aad19;
  color: white;
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  border: none;
}

.tf-open-modal {
  background: white;
  text-align: center;
  padding-bottom: 30px;
}
.tf-open-header {
  background: #f1f1f1;
  border: none;
}
.tf-open-icon img {
  width: 50px;
  height: 50px;
  margin-top: 20px;
}
.tf-open-status {
  font-size: 18px;
  margin-top: 15px;
}
.tf-open-amount {
  font-size: 36px;
  font-weight: bold;
  margin-top: 10px;
}
.tf-open-remark {
  color: #888;
  margin-top: 10px;
  font-size: 14px;
}
.tf-open-action {
  margin-top: 30px;
  color: #576b95;
  cursor: pointer;
}

/* Chat Message Bubbles for RP & TF */
.msg-bubble.red-packet-bubble {
  background: #fa9d3b;
  color: white;
  padding: 0;
  border-radius: 8px;
  overflow: hidden;
  width: 220px;
  cursor: pointer;
  border: none;
}
.msg-bubble.red-packet-bubble.my-msg {
  background: #fa9d3b;
}
.rp-bubble-top {
  display: flex;
  align-items: center;
  padding: 12px 15px;
}
.rp-bubble-icon {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}
.rp-bubble-text {
  font-size: 15px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rp-bubble-bottom {
  background: rgba(255,255,255,0.2);
  padding: 4px 15px;
  font-size: 12px;
}

.msg-bubble.transfer-bubble {
  background: #fa9d3b;
  color: white;
  padding: 0;
  border-radius: 8px;
  overflow: hidden;
  width: 220px;
  cursor: pointer;
  border: none;
}
.msg-bubble.transfer-bubble.my-msg {
  background: #fa9d3b;
}
.tf-bubble-top {
  display: flex;
  align-items: center;
  padding: 12px 15px;
}
.tf-bubble-icon {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}
.tf-bubble-info {
  flex: 1;
}
.tf-bubble-amount {
  font-size: 16px;
}
.tf-bubble-remark {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 2px;
}
.tf-bubble-bottom {
  background: rgba(255,255,255,0.2);
  padding: 4px 15px;
  font-size: 12px;
}
    """

    if ".red-packet-modal" not in chat_css:
        chat_css += "\n" + css_additions
        write_file(CHAT_CSS, chat_css)
        print("CSS injected into chat.css")

    print("Reading main.js...")
    main_js = read_file(MAIN_JS)
    
    js_additions = """
// --- Red Packet & Transfer Logic ---

let currentRpCover = null;
let activeRedPacketId = null;
let activeTransferId = null;

function showRedPacketModal() {
  document.getElementById('redPacketSendModal').style.display = 'flex';
  document.getElementById('rpAmount').value = '';
  document.getElementById('rpAmountDisplay').innerText = '0.00';
  document.getElementById('rpGreeting').value = '恭喜发财，大吉大利';
  currentRpCover = null;
  document.getElementById('rpCoverPreview').style.backgroundImage = "url('ICON/红包.png')";
  loadRpCoverHistory();
}

function showTransferModal() {
  document.getElementById('transferSendModal').style.display = 'flex';
  document.getElementById('tfAmount').value = '';
  document.getElementById('tfRemark').value = '转账';
}

document.getElementById('rpAmount').addEventListener('input', function() {
  let val = parseFloat(this.value);
  document.getElementById('rpAmountDisplay').innerText = isNaN(val) ? '0.00' : val.toFixed(2);
});

async function handleRpCover(input) {
  const file = input.files?.[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = e => {
    const img = new Image();
    img.onload = async () => {
      // 3:4 crop
      const canvas = document.createElement('canvas');
      let targetW = img.width;
      let targetH = targetW * 4 / 3;
      if (targetH > img.height) {
        targetH = img.height;
        targetW = targetH * 3 / 4;
      }
      const startX = (img.width - targetW) / 2;
      const startY = (img.height - targetH) / 2;
      
      const maxSize = 800;
      let finalW = targetW;
      let finalH = targetH;
      if (finalH > maxSize) {
        finalH = maxSize;
        finalW = finalH * 3 / 4;
      }
      
      canvas.width = finalW;
      canvas.height = finalH;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, startX, startY, targetW, targetH, 0, 0, finalW, finalH);
      
      const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
      currentRpCover = dataUrl;
      document.getElementById('rpCoverPreview').style.backgroundImage = `url('${dataUrl}')`;
      
      // Save to IndexedDB images
      if (window.addExtImage) {
         try {
           await window.addExtImage(dataUrl);
         } catch(e){}
      }
      loadRpCoverHistory();
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function loadRpCoverHistory() {
  const historyContainer = document.getElementById('rpCoverHistory');
  if(!historyContainer) return;
  historyContainer.innerHTML = '';
  if (window.getAllExtImages) {
    try {
      const imgs = await window.getAllExtImages();
      // Show latest 5
      imgs.slice(-5).reverse().forEach(imgRecord => {
        const imgEl = document.createElement('img');
        imgEl.src = imgRecord.data;
        imgEl.onclick = () => {
           currentRpCover = imgRecord.data;
           document.getElementById('rpCoverPreview').style.backgroundImage = `url('${imgRecord.data}')`;
           Array.from(historyContainer.children).forEach(c => c.classList.remove('selected'));
           imgEl.classList.add('selected');
        };
        historyContainer.appendChild(imgEl);
      });
    } catch(e){}
  }
}

async function sendRedPacket() {
  const amount = parseFloat(document.getElementById('rpAmount').value);
  if (isNaN(amount) || amount <= 0) {
    alert('请输入有效金额');
    return;
  }
  const greeting = document.getElementById('rpGreeting').value || '恭喜发财，大吉大利';
  
  const msgObj = {
    id: Date.now().toString(),
    senderId: currentSenderId,
    type: 'red_packet',
    content: JSON.stringify({ amount: amount, greeting: greeting, cover: currentRpCover, opened: false }),
    timestamp: new Date().toISOString()
  };
  
  document.getElementById('redPacketSendModal').style.display = 'none';
  await appendMessageToUI(msgObj);
}

async function sendTransfer() {
  const amount = parseFloat(document.getElementById('tfAmount').value);
  if (isNaN(amount) || amount <= 0) {
    alert('请输入有效金额');
    return;
  }
  const remark = document.getElementById('tfRemark').value || '转账';
  
  const msgObj = {
    id: Date.now().toString(),
    senderId: currentSenderId,
    type: 'transfer',
    content: JSON.stringify({ amount: amount, remark: remark, received: false }),
    timestamp: new Date().toISOString()
  };
  
  document.getElementById('transferSendModal').style.display = 'none';
  await appendMessageToUI(msgObj);
}

function clickRedPacket(id, contentStr, isMine) {
  const data = JSON.parse(contentStr);
  activeRedPacketId = id;
  const modal = document.getElementById('redPacketOpenModal');
  const contentEl = document.getElementById('rpOpenContent');
  const nameEl = document.getElementById('rpOpenName');
  const greetingEl = document.getElementById('rpOpenGreeting');
  const amountBox = document.getElementById('rpOpenAmountBox');
  const amountEl = document.getElementById('rpOpenAmount');
  const btnEl = document.getElementById('rpOpenBtn');
  
  modal.style.display = 'flex';
  nameEl.innerText = isMine ? '我' : (activeContact ? activeContact.name : '对方');
  greetingEl.innerText = data.greeting;
  
  if (data.cover) {
    contentEl.style.backgroundImage = `url('${data.cover}')`;
    contentEl.classList.add('has-custom-cover');
  } else {
    contentEl.style.backgroundImage = 'none';
    contentEl.classList.remove('has-custom-cover');
  }
  
  if (data.opened) {
    amountBox.style.display = 'block';
    amountEl.innerText = data.amount.toFixed(2);
    btnEl.style.display = 'none';
  } else {
    amountBox.style.display = 'none';
    btnEl.style.display = 'block';
  }
}

async function openRedPacket() {
  if (!activeRedPacketId) return;
  const btnEl = document.getElementById('rpOpenBtn');
  btnEl.style.transform = 'rotateY(360deg)';
  btnEl.style.transition = 'transform 0.5s';
  
  setTimeout(async () => {
    // Update msg in DB
    const msgs = await window.getChatMessages(activeContact.id);
    const msgIndex = msgs.findIndex(m => m.id === activeRedPacketId);
    if (msgIndex !== -1) {
      const data = JSON.parse(msgs[msgIndex].content);
      data.opened = true;
      msgs[msgIndex].content = JSON.stringify(data);
      await window.saveChatMessages(activeContact.id, msgs);
      
      // Update UI manually or re-render
      const amountBox = document.getElementById('rpOpenAmountBox');
      const amountEl = document.getElementById('rpOpenAmount');
      amountBox.style.display = 'block';
      amountEl.innerText = data.amount.toFixed(2);
      btnEl.style.display = 'none';
      
      // Update bubble in chat
      const bubble = document.querySelector(`.msg-item[data-id="${activeRedPacketId}"] .msg-bubble`);
      if (bubble) {
        bubble.style.opacity = '0.7';
      }
    }
  }, 600);
}

function clickTransfer(id, contentStr, isMine) {
  const data = JSON.parse(contentStr);
  activeTransferId = id;
  const modal = document.getElementById('transferOpenModal');
  document.getElementById('tfOpenAmount').innerText = data.amount.toFixed(2);
  document.getElementById('tfOpenRemark').innerText = data.remark;
  
  const statusEl = document.getElementById('tfOpenStatus');
  const actionEl = document.getElementById('tfOpenAction');
  
  if (data.received) {
    statusEl.innerText = '已收款';
    actionEl.style.display = 'none';
  } else {
    if (isMine) {
      statusEl.innerText = '待对方收款';
      actionEl.style.display = 'none';
    } else {
      statusEl.innerText = '待收款';
      actionEl.style.display = 'block';
    }
  }
  
  modal.style.display = 'flex';
}

async function acceptTransfer() {
  if (!activeTransferId) return;
  const msgs = await window.getChatMessages(activeContact.id);
  const msgIndex = msgs.findIndex(m => m.id === activeTransferId);
  if (msgIndex !== -1) {
    const data = JSON.parse(msgs[msgIndex].content);
    data.received = true;
    msgs[msgIndex].content = JSON.stringify(data);
    await window.saveChatMessages(activeContact.id, msgs);
    
    document.getElementById('tfOpenStatus').innerText = '已收款';
    document.getElementById('tfOpenAction').style.display = 'none';
    
    // Update bubble in chat
    const bubble = document.querySelector(`.msg-item[data-id="${activeTransferId}"] .tf-bubble-remark`);
    if (bubble) {
      bubble.innerText = '已收款';
    }
  }
}
// --- End Red Packet & Transfer ---
"""

    if "showRedPacketModal" not in main_js:
        main_js += "\n" + js_additions
        write_file(MAIN_JS, main_js)
        print("JS functions added to main.js")

    # Now we need to modify selectFile and createMsgElement
    # Modify selectFile
    if "t === 'image'" in main_js and "t === 'red_packet'" not in main_js:
        # replace:
        # if (t === 'image') {
        #   document.getElementById('chat-img-input').click();
        # } else {
        #   alert('未实现'+t); 
        # }
        main_js = re.sub(
            r"(if\s*\(t\s*===\s*'image'\)\s*\{\s*document\.getElementById\('chat-img-input'\)\.click\(\);\s*\})",
            r"\1 else if (t === 'red_packet') { showRedPacketModal(); } else if (t === 'transfer') { showTransferModal(); }",
            main_js
        )
        write_file(MAIN_JS, main_js)
        print("Updated selectFile")

    # Modify createMsgElement
    if "type === 'red_packet'" not in main_js:
        # find where it switches type
        # In main.js it's probably around:
        # if (type === 'image') {
        #   const img = document.createElement('img');
        # ...
        # We need to insert handlers for red_packet and transfer.
        create_msg_target = r"(if\s*\(type\s*===\s*'image'\)\s*\{[^\}]+?(?:\}\s*else\s*if\s*\(type\s*===\s*'audio'\)\s*\{[^\}]+\})?\s*\})"
        replacement = r"""\1 else if (type === 'red_packet') {
    const data = JSON.parse(content);
    bubble.className += ' red-packet-bubble';
    bubble.style.opacity = data.opened ? '0.7' : '1';
    bubble.innerHTML = `
      <div class="rp-bubble-top">
        <img src="ICON/红包.png" class="rp-bubble-icon">
        <div class="rp-bubble-text">${data.greeting || '恭喜发财，大吉大利'}</div>
      </div>
      <div class="rp-bubble-bottom">微信红包</div>
    `;
    bubble.onclick = () => clickRedPacket(msg.id, content, isMine);
  } else if (type === 'transfer') {
    const data = JSON.parse(content);
    bubble.className += ' transfer-bubble';
    bubble.style.opacity = data.received ? '0.7' : '1';
    bubble.innerHTML = `
      <div class="tf-bubble-top">
        <img src="ICON/转账.png" class="tf-bubble-icon">
        <div class="tf-bubble-info">
          <div class="tf-bubble-amount">￥${data.amount.toFixed(2)}</div>
          <div class="tf-bubble-remark">${data.received ? '已收款' : data.remark}</div>
        </div>
      </div>
      <div class="tf-bubble-bottom">微信转账</div>
    `;
    bubble.onclick = () => clickTransfer(msg.id, content, isMine);
  }"""
        main_js = re.sub(create_msg_target, replacement, main_js)
        write_file(MAIN_JS, main_js)
        print("Updated createMsgElement")

if __name__ == '__main__':
    main()
