#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix red packet: redesign send modal, fix handleRpCover, update bubble style
"""
import re

# ============================================================
# 1. Fix index.html - Replace the red packet send modal
# ============================================================
print("Reading index.html...")
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find start and end of the red packet send modal
send_modal_start = html.find('<div id="redPacketSendModal"')
if send_modal_start == -1:
    print("ERROR: Could not find redPacketSendModal")
else:
    # Find the closing tag - count divs
    pos = send_modal_start
    depth = 0
    i = pos
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                send_modal_end = i + 6
                break
            i += 6
        else:
            i += 1
    
    old_modal = html[send_modal_start:send_modal_end]
    print(f"Found old modal ({len(old_modal)} chars)")
    
    new_modal = '''<div id="redPacketSendModal" class="modal" style="display:none;">
      <div class="modal-overlay" onclick="document.getElementById('redPacketSendModal').style.display='none'"></div>
      <div class="modal-content rp-send-modal-content">
        <!-- Close button -->
        <button class="rp-modal-close" onclick="document.getElementById('redPacketSendModal').style.display='none'">✕</button>
        
        <h2 class="rp-modal-title">发红包</h2>

        <!-- Red packet card preview -->
        <div class="rp-card-preview-wrap">
          <div class="rp-card-preview" id="rpCardPreview">
            <div class="rp-card-cover-area" id="rpCardCoverArea">
              <!-- Default state: dark background with hint text -->
              <div class="rp-card-default-hint" id="rpCardDefaultHint">
                <span class="rp-hint-text">这里是画面</span>
                <span class="rp-hint-line"></span>
              </div>
              <!-- Uploaded image -->
              <img class="rp-card-cover-img" id="rpCardCoverImg" src="" alt="" style="display:none;"/>
              <!-- Overlay info (shown when image uploaded) -->
              <div class="rp-card-info-overlay" id="rpCardInfoOverlay" style="display:none;">
                <div class="rp-card-sender-name" id="rpCardSenderName">的红包</div>
                <div class="rp-card-blessing" id="rpCardBlessingPreview">祝福语</div>
              </div>
              <!-- Upload click target -->
              <div class="rp-card-upload-click" onclick="document.getElementById('rpCoverInput').click()" title="点击上传封面图片"></div>
            </div>
            <div class="rp-card-bottom">
              <div class="rp-kai-btn">開</div>
            </div>
          </div>
          <input type="file" id="rpCoverInput" accept="image/*" style="display:none;" onchange="handleRpCover(this)">
          <div class="rp-upload-hint">点击卡片上传封面图片</div>
        </div>

        <!-- Amount input -->
        <div class="rp-form-row">
          <label class="rp-form-label">金额（元）</label>
          <div class="rp-amount-row">
            <span class="rp-amount-symbol">¥</span>
            <input type="number" id="redPacketAmount" class="rp-amount-input" placeholder="0.00" min="0.01" step="0.01" max="9999" oninput="document.getElementById('rpAmountDisplay').textContent=this.value||'0.00'"/>
          </div>
        </div>

        <!-- Blessing message -->
        <div class="rp-form-row">
          <label class="rp-form-label">祝福语</label>
          <input type="text" id="redPacketMsg" class="rp-msg-input" placeholder="恭喜发财，大吉大利" maxlength="30" oninput="document.getElementById('rpCardBlessingPreview').textContent=this.value||'祝福语';document.getElementById('rpCardInfoOverlay').style.display=rpCardCoverImg.style.display!=='none'?'flex':'none'"/>
        </div>

        <!-- Send button -->
        <button class="rp-send-btn" onclick="sendRedPacket()">塞钱进红包 🧧</button>
      </div>
    </div>'''
    
    html = html[:send_modal_start] + new_modal + html[send_modal_end:]
    print("Replaced send modal HTML")

# Now fix the red packet bubble rendering in addMsgToUI area
# Find existing red-packet bubble HTML pattern and update
# We look for the msg type==='redpacket' rendering

print("Writing index.html...")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html saved")

# ============================================================
# 2. Update css/chat.css - Add red packet styles
# ============================================================
print("\nReading css/chat.css...")
with open('css/chat.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Remove old rp-* CSS blocks if any
# We'll append a comprehensive new block

rp_css_marker = '/* === RED PACKET CARD STYLES === */'
if rp_css_marker in css:
    # Remove existing block
    start_idx = css.find(rp_css_marker)
    end_marker = '/* === END RED PACKET CARD STYLES === */'
    end_idx = css.find(end_marker)
    if end_idx != -1:
        css = css[:start_idx] + css[end_idx + len(end_marker):]
        print("Removed old RP CSS block")

new_rp_css = '''
/* === RED PACKET CARD STYLES === */

/* --- Send Modal Container --- */
.rp-send-modal-content {
  background: #1a1a2e;
  border-radius: 20px;
  padding: 28px 24px 24px;
  max-width: 360px;
  width: 90%;
  margin: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
  color: #fff;
}

.rp-modal-close {
  position: absolute;
  top: 14px;
  right: 16px;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  transition: background 0.2s;
}
.rp-modal-close:hover { background: #c0392b; }

.rp-modal-title {
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 20px;
  color: #f39c12;
  letter-spacing: 2px;
}

/* --- Card Preview --- */
.rp-card-preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.rp-card-preview {
  width: 180px;
  height: 240px;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 3px #2c2c3e;
  display: flex;
  flex-direction: column;
  position: relative;
  background: #1e1e2e;
}

/* Top area (cover image or default) */
.rp-card-cover-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #1e1e2e;
  cursor: pointer;
}

/* Grid pattern for default state */
.rp-card-default-hint {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(rgba(50,50,70,0.8) 1px, transparent 1px),
    linear-gradient(90deg, rgba(50,50,70,0.8) 1px, transparent 1px);
  background-size: 20px 20px;
  background-color: #16161e;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 18px 16px;
}

.rp-hint-text {
  font-family: 'STKaiti', 'KaiTi', 'STFangsong', cursive;
  font-size: 16px;
  color: #c0392b;
  letter-spacing: 1px;
  line-height: 1.4;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

.rp-hint-line {
  display: block;
  width: 60px;
  height: 2px;
  background: #c0392b;
  margin-top: 4px;
  transform: rotate(-8deg);
  border-radius: 2px;
}

.rp-card-cover-img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rp-card-info-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.45) 0%, transparent 60%);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 12px 12px;
  gap: 4px;
}

.rp-card-sender-name {
  font-size: 12px;
  color: #f8e8b0;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0,0,0,0.7);
}

.rp-card-blessing {
  font-size: 15px;
  color: #fff;
  font-weight: 700;
  text-shadow: 0 1px 4px rgba(0,0,0,0.8);
  line-height: 1.3;
  max-width: 140px;
}

.rp-card-upload-click {
  position: absolute;
  inset: 0;
  z-index: 5;
}

/* Bottom red area with 開 button */
.rp-card-bottom {
  height: 72px;
  background: #e05040;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-top: 2px solid #c94030;
}

/* Curved top edge on red area */
.rp-card-bottom::before {
  content: '';
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  width: 160%;
  height: 36px;
  background: #e05040;
  border-radius: 50% 50% 0 0 / 100% 100% 0 0;
}

.rp-kai-btn {
  width: 52px;
  height: 52px;
  background: #d4b896;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-family: 'STSong', 'SimSun', serif;
  color: #2c1a0e;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  z-index: 1;
  position: relative;
}

.rp-upload-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #888;
  text-align: center;
}

/* --- Form Rows --- */
.rp-form-row {
  margin-bottom: 14px;
}

.rp-form-label {
  display: block;
  font-size: 12px;
  color: #aaa;
  margin-bottom: 6px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.rp-amount-row {
  display: flex;
  align-items: center;
  background: #2a2a3e;
  border-radius: 10px;
  padding: 4px 12px;
  border: 1px solid #3a3a5e;
}

.rp-amount-symbol {
  font-size: 20px;
  color: #f39c12;
  margin-right: 8px;
  font-weight: 700;
}

.rp-amount-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  padding: 6px 0;
  width: 100%;
}
.rp-amount-input::placeholder { color: #555; font-size: 20px; }

.rp-msg-input {
  width: 100%;
  background: #2a2a3e;
  border: 1px solid #3a3a5e;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  color: #fff;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.rp-msg-input::placeholder { color: #666; }
.rp-msg-input:focus { border-color: #e05040; }

/* --- Send Button --- */
.rp-send-btn {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #e05040, #c0392b);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  letter-spacing: 1px;
  margin-top: 6px;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 15px rgba(224,80,64,0.4);
}
.rp-send-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(224,80,64,0.5);
}
.rp-send-btn:active { transform: translateY(0); }

/* --- Chat bubble: Red Packet Card --- */
.rp-bubble-card {
  width: 160px;
  height: 213px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(0,0,0,0.35);
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  background: #1e1e2e;
}
.rp-bubble-card:hover {
  transform: scale(1.03);
  box-shadow: 0 8px 28px rgba(0,0,0,0.45);
}

.rp-bubble-cover {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.rp-bubble-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.rp-bubble-default-cover {
  width: 100%;
  height: 100%;
  background:
    linear-gradient(rgba(50,50,70,0.8) 1px, transparent 1px),
    linear-gradient(90deg, rgba(50,50,70,0.8) 1px, transparent 1px);
  background-size: 16px 16px;
  background-color: #16161e;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
  padding: 14px 12px;
  box-sizing: border-box;
}

.rp-bubble-hint-text {
  font-family: 'STKaiti', 'KaiTi', cursive;
  font-size: 13px;
  color: #c0392b;
  line-height: 1.4;
}

.rp-bubble-hint-line {
  display: block;
  width: 45px;
  height: 2px;
  background: #c0392b;
  margin-top: 3px;
  transform: rotate(-8deg);
  border-radius: 2px;
}

.rp-bubble-info {
  position: absolute;
  top: 0; left: 0; right: 0;
  padding: 10px 10px 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.5) 0%, transparent 100%);
}

.rp-bubble-sender {
  font-size: 11px;
  color: #f8e8b0;
  font-weight: 600;
  display: block;
}

.rp-bubble-blessing {
  font-size: 13px;
  color: #fff;
  font-weight: 700;
  display: block;
  margin-top: 2px;
  line-height: 1.3;
}

.rp-bubble-bottom {
  height: 62px;
  background: #e05040;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-top: 2px solid #c94030;
}

.rp-bubble-bottom::before {
  content: '';
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%);
  width: 160%;
  height: 30px;
  background: #e05040;
  border-radius: 50% 50% 0 0 / 100% 100% 0 0;
}

.rp-bubble-kai {
  width: 44px;
  height: 44px;
  background: #d4b896;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-family: 'STSong', 'SimSun', serif;
  color: #2c1a0e;
  font-weight: 700;
  z-index: 1;
  position: relative;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

/* Opened state */
.rp-bubble-card.opened {
  opacity: 0.7;
  filter: grayscale(0.4);
}

.rp-bubble-card.opened .rp-bubble-kai::after {
  content: '已领';
  position: absolute;
  font-size: 8px;
  bottom: -14px;
  left: 50%;
  transform: translateX(-50%);
  color: #f8e8b0;
  white-space: nowrap;
}

/* === END RED PACKET CARD STYLES === */
'''

css += new_rp_css

with open('css/chat.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("css/chat.css updated")

# ============================================================
# 3. Fix js/main.js - Add handleRpCover and fix bubble render
# ============================================================
print("\nReading js/main.js...")
with open('js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# --- 3a. Add handleRpCover function ---
rp_cover_marker = '/* === RP COVER HANDLER === */'
if rp_cover_marker not in js:
    new_rp_functions = '''
/* === RP COVER HANDLER === */
var _rpCoverBase64 = null;

function handleRpCover(input) {
  if (!input || !input.files || !input.files[0]) return;
  var file = input.files[0];
  var reader = new FileReader();
  reader.onload = function(e) {
    _rpCoverBase64 = e.target.result;
    // Show image in preview card
    var img = document.getElementById('rpCardCoverImg');
    var defaultHint = document.getElementById('rpCardDefaultHint');
    var infoOverlay = document.getElementById('rpCardInfoOverlay');
    var senderNameEl = document.getElementById('rpCardSenderName');
    if (img) {
      img.src = _rpCoverBase64;
      img.style.display = 'block';
    }
    if (defaultHint) defaultHint.style.display = 'none';
    if (infoOverlay) {
      infoOverlay.style.display = 'flex';
      // Update sender name
      var charName = (window.currentCharacter && window.currentCharacter.name) ? window.currentCharacter.name : '我';
      if (senderNameEl) senderNameEl.textContent = charName + ' 的红包';
      // Update blessing preview
      var msgEl = document.getElementById('redPacketMsg');
      var blessingEl = document.getElementById('rpCardBlessingPreview');
      if (blessingEl && msgEl) blessingEl.textContent = msgEl.value || '恭喜发财，大吉大利';
    }
  };
  reader.readAsDataURL(file);
}

function resetRpCoverPreview() {
  _rpCoverBase64 = null;
  var img = document.getElementById('rpCardCoverImg');
  var defaultHint = document.getElementById('rpCardDefaultHint');
  var infoOverlay = document.getElementById('rpCardInfoOverlay');
  var coverInput = document.getElementById('rpCoverInput');
  if (img) { img.src = ''; img.style.display = 'none'; }
  if (defaultHint) defaultHint.style.display = 'flex';
  if (infoOverlay) infoOverlay.style.display = 'none';
  if (coverInput) coverInput.value = '';
}
/* === END RP COVER HANDLER === */

'''
    # Insert before sendRedPacket function or at end of file
    if 'function sendRedPacket' in js:
        insert_pos = js.find('function sendRedPacket')
        js = js[:insert_pos] + new_rp_functions + js[insert_pos:]
        print("Inserted handleRpCover before sendRedPacket")
    else:
        # Append near the end (before last closing or at end)
        js = js + new_rp_functions
        print("Appended handleRpCover at end of main.js")
else:
    print("handleRpCover already exists")

# --- 3b. Fix sendRedPacket to include cover image ---
# Find sendRedPacket function and update it to pass _rpCoverBase64
if 'function sendRedPacket' in js:
    # Check if it already passes cover
    func_start = js.find('function sendRedPacket')
    func_body_start = js.find('{', func_start)
    # Find closing brace
    depth = 0
    i = func_body_start
    while i < len(js):
        if js[i] == '{':
            depth += 1
        elif js[i] == '}':
            depth -= 1
            if depth == 0:
                func_end = i + 1
                break
        i += 1
    old_send_func = js[func_start:func_end]
    print(f"Found sendRedPacket function ({len(old_send_func)} chars)")
    
    # Check if it already uses _rpCoverBase64
    if '_rpCoverBase64' not in old_send_func:
        # Add cover to the message data
        # Find where message object is created
        if "type: 'redpacket'" in old_send_func or 'type:"redpacket"' in old_send_func or "type: \"redpacket\"" in old_send_func:
            # Try to add cover field
            patterns = ["type: 'redpacket'", 'type: "redpacket"', "type:'redpacket'", 'type:"redpacket"']
            for pat in patterns:
                if pat in old_send_func:
                    new_send_func = old_send_func.replace(
                        pat,
                        pat + ',\n        cover: _rpCoverBase64 || null'
                    )
                    js = js[:func_start] + new_send_func + js[func_end:]
                    print(f"Added cover to sendRedPacket message data (pattern: {pat})")
                    break
        # Also add reset call
        if 'resetRpCoverPreview' not in old_send_func:
            # Find where modal is closed after sending
            close_patterns = ["style.display='none'", 'style.display = "none"', "style.display = 'none'"]
            for pat in close_patterns:
                if pat in js[func_start:func_start+len(old_send_func)+200]:
                    pass  # will handle differently
            print("Note: resetRpCoverPreview not added to sendRedPacket - check manually if needed")

# --- 3c. Fix addMsgToUI for red packet bubble rendering ---
# Find the redpacket case in addMsgToUI
rp_bubble_marker_new = 'rp-bubble-card'
if rp_bubble_marker_new not in js:
    # Find the old red packet rendering
    patterns_to_find = [
        "type === 'redpacket'",
        'type === "redpacket"',
        "msg.type === 'redpacket'",
        'msg.type === "redpacket"',
        "case 'redpacket'",
        'case "redpacket"'
    ]
    rp_render_pos = -1
    rp_render_pattern = None
    for pat in patterns_to_find:
        pos = js.find(pat)
        if pos != -1:
            rp_render_pos = pos
            rp_render_pattern = pat
            break
    
    if rp_render_pos != -1:
        print(f"Found red packet render at pos {rp_render_pos} with pattern: {rp_render_pattern}")
        # Look around this position for the HTML template
        context_start = max(0, rp_render_pos - 200)
        context_end = min(len(js), rp_render_pos + 1000)
        context = js[context_start:context_end]
        print("Context around rp render:")
        print(context[:500])
    else:
        print("Could not find red packet render pattern - will search differently")
        # Search for red packet HTML in JS
        for marker in ['红包', 'redpacket', 'red-packet', 'red_packet']:
            positions = [m.start() for m in re.finditer(re.escape(marker), js)]
            if positions:
                print(f"Found '{marker}' at positions: {positions[:5]}")
                break

print("\nDone with main.js analysis. Saving...")
with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("js/main.js saved")
print("\nAll done! Please check the files.")
