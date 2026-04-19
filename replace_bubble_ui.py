
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''    <div class="sub-page" id="theme-bubble-setting">

      <div class="page-header">
        <div class="page-back" onclick="closeSub(\'theme-bubble-setting\')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">气泡颜色</div>
      </div>
      <div class="page-body">

        <div class="form-label">气泡颜色</div>
        <div class="setting-desc" style="margin-top:6px;margin-bottom:12px;">调整双方气泡的颜色、透明度和圆角。</div>

        <div style="padding: 25px 15px; background: rgba(0,0,0,0.03); border-radius: 12px; margin-bottom: 20px; display: flex; flex-direction: column; gap: 20px; border: 1px dashed var(--light-pink); overflow: hidden;">
          <div class="msg-item left" style="align-self: flex-start; max-width: 80%;">
            <div class="msg-avatar" style="border:none;"><img src="haibaologo.png" style="border-radius:50%;"></div>
            <div class="msg-bubble" style="pointer-events: none;">对方气泡预览</div>
          </div>
          <div class="msg-item right" style="align-self: flex-end; max-width: 80%;">
            <div class="msg-avatar" style="border:none;"><img src="haibaologo.png" style="border-radius:50%;"></div>
            <div class="msg-bubble" style="pointer-events: none;">我的气泡预览</div>
          </div>
        </div>

        <div style="display:flex; gap:10px;">
          <div class="form-section" style="flex:1;">
            <div class="form-label" style="font-size:13px;">对方气泡颜色</div>
            <div style="display:flex; align-items:center; gap:10px;">
              <input type="color" id="leftBubbleColor" value="#ffffff" onchange="document.getElementById(\'leftBubbleColorHex\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="width:50px;height:36px;border:none;cursor:pointer;border-radius:8px;padding:0;">
              <input type="text" id="leftBubbleColorHex" value="#ffffff" onchange="document.getElementById(\'leftBubbleColor\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="width:80px;height:36px;border:1px solid var(--light-pink);border-radius:8px;padding:0 10px;font-size:14px;outline:none;" placeholder="#HEX">
            </div>
          </div>

          <div class="form-section" style="flex:1;">
            <div class="form-label" style="font-size:13px;">我的气泡颜色</div>
            <div style="display:flex; align-items:center; gap:10px;">
              <input type="color" id="rightBubbleColor" value="#f0b8c8" onchange="document.getElementById(\'rightBubbleColorHex\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="width:50px;height:36px;border:none;cursor:pointer;border-radius:8px;padding:0;">
              <input type="text" id="rightBubbleColorHex" value="#f0b8c8" onchange="document.getElementById(\'rightBubbleColor\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="width:80px;height:36px;border:1px solid var(--light-pink);border-radius:8px;padding:0 10px;font-size:14px;outline:none;" placeholder="#HEX">
            </div>
          </div>
        </div>

        <div style="margin-top:15px;">
          <div style="font-size:13px; color:var(--text-main); margin-bottom:8px; font-weight:500;">气泡角度 <span id="bubbleRadiusValue">12</span>px</div>
          <input type="range" id="bubbleRadius" min="0" max="30" step="1" value="12" oninput="applyBubbleSettings(); updateBubblePreview();" style="width:100%;">
        </div>
        <div style="margin-top:15px; margin-bottom:20px;">
          <div style="font-size:13px; color:var(--text-main); margin-bottom:8px; font-weight:500;">透明度 <span id="bubbleOpacityValue">1.0</span></div>
          <input type="range" id="bubbleOpacity" min="0.1" max="1" step="0.1" value="1.0" oninput="applyBubbleSettings(); updateBubblePreview();" style="width:100%;">
        </div>

        <div class="form-section">
          <div class="form-label" style="font-size:13px;">对方气泡装饰</div>
          <div style="display:flex; align-items:center; gap:10px;">
            <div id="leftDecPreview" style="width:40px; height:40px; border:1px dashed #ccc; border-radius:8px; background-size:contain; background-repeat:no-repeat; background-position:center;"></div>
            <label class="upload-btn" style="margin:0;">上传<input type="file" accept="image/png" onchange="uploadBubbleDec(this, \'left\')" style="display:none;"></label>
            <button class="upload-btn" style="margin:0;" onclick="clearBubbleDec(\'left\')">清除</button>
            <select id="leftDecCorner" onchange="applyBubbleDecSettings()" class="form-input" style="width:auto; padding:4px 8px; margin:0;">
              <option value="top-left">左上角</option>
              <option value="top-right">右上角</option>
              <option value="bottom-left">左下角</option>
              <option value="bottom-right">右下角</option>
            </select>
          </div>
          <div style="margin-top:10px;">
            <div style="font-size:12px; color:var(--text-light);">大小 <span id="leftDecSizeValue">30</span>px</div>
            <input type="range" id="leftDecSize" min="10" max="100" step="1" value="30" oninput="applyBubbleDecSettings()" style="width:100%;">
          </div>
          <div style="margin-top:5px; display:flex; gap:10px;">
            <div style="flex:1;">
              <div style="font-size:12px; color:var(--text-light);">垂直偏移 <span id="leftDecYValue">-10</span>px</div>
              <input type="range" id="leftDecY" min="-15" max="15" step="1" value="-10" oninput="applyBubbleDecSettings()" style="width:100%;">
            </div>
            <div style="flex:1;">
              <div style="font-size:12px; color:var(--text-light);">水平偏移 <span id="leftDecXValue">-5</span>px</div>
              <input type="range" id="leftDecX" min="-15" max="15" step="1" value="-5" oninput="applyBubbleDecSettings()" style="width:100%;">
            </div>
          </div>
        </div>

        <div class="form-section">
          <div class="form-label" style="font-size:13px;">我的气泡装饰</div>
          <div style="display:flex; align-items:center; gap:10px;">
            <div id="rightDecPreview" style="width:40px; height:40px; border:1px dashed #ccc; border-radius:8px; background-size:contain; background-repeat:no-repeat; background-position:center;"></div>
            <label class="upload-btn" style="margin:0;">上传<input type="file" accept="image/png" onchange="uploadBubbleDec(this, \'right\')" style="display:none;"></label>
            <button class="upload-btn" style="margin:0;" onclick="clearBubbleDec(\'right\')">清除</button>
            <select id="rightDecCorner" onchange="applyBubbleDecSettings()" class="form-input" style="width:auto; padding:4px 8px; margin:0;">
              <option value="top-left">左上角</option>
              <option value="top-right" selected>右上角</option>
              <option value="bottom-left">左下角</option>
              <option value="bottom-right">右下角</option>
            </select>
          </div>
          <div style="margin-top:10px;">
            <div style="font-size:12px; color:var(--text-light);">大小 <span id="rightDecSizeValue">30</span>px</div>
            <input type="range" id="rightDecSize" min="10" max="100" step="1" value="30" oninput="applyBubbleDecSettings()" style="width:100%;">
          </div>
          <div style="margin-top:5px; display:flex; gap:10px;">
            <div style="flex:1;">
              <div style="font-size:12px; color:var(--text-light);">垂直偏移 <span id="rightDecYValue">-10</span>px</div>
              <input type="range" id="rightDecY" min="-15" max="15" step="1" value="-10" oninput="applyBubbleDecSettings()" style="width:100%;">
            </div>
            <div style="flex:1;">
              <div style="font-size:12px; color:var(--text-light);">水平偏移 <span id="rightDecXValue">-10</span>px</div>
              <input type="range" id="rightDecX" min="-15" max="15" step="1" value="-10" oninput="applyBubbleDecSettings()" style="width:100%;">
            </div>
          </div>
        </div>
        </div>
      </div>
    </div>'''

NEW = '''    <div class="sub-page" id="theme-bubble-setting">
      <div class="page-header">
        <div class="page-back" onclick="closeSub(\'theme-bubble-setting\')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">气泡样式</div>
      </div>
      <div class="page-body" style="padding:0 0 32px 0;">

        <!-- 预览区 -->
        <div style="background:linear-gradient(135deg,#f8f0ff 0%,#fce4ec 100%); padding:20px 18px 16px; margin-bottom:0; position:relative; overflow:hidden;">
          <div style="font-size:11px; color:#b09ab8; letter-spacing:1px; text-transform:uppercase; margin-bottom:12px; font-weight:600;">PREVIEW</div>
          <div class="msg-item left" style="align-self:flex-start; max-width:78%; margin-bottom:10px;">
            <div class="msg-avatar" style="border:none;"><img src="haibaologo.png" style="border-radius:50%;width:32px;height:32px;"></div>
            <div class="msg-bubble" style="pointer-events:none; font-size:13px;">对方气泡预览</div>
          </div>
          <div class="msg-item right" style="align-self:flex-end; max-width:78%; justify-content:flex-end;">
            <div class="msg-bubble" style="pointer-events:none; font-size:13px;">我的气泡预览</div>
            <div class="msg-avatar" style="border:none;"><img src="haibaologo.png" style="border-radius:50%;width:32px;height:32px;"></div>
          </div>
          <div style="position:absolute;right:-18px;top:-18px;width:80px;height:80px;border-radius:50%;background:rgba(255,255,255,0.18);pointer-events:none;"></div>
        </div>

        <!-- 颜色区 -->
        <div style="padding:18px 16px 0;">
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:18px;">
            <!-- 对方气泡颜色 -->
            <div style="background:#fff; border-radius:14px; padding:14px; box-shadow:0 2px 10px rgba(0,0,0,0.06);">
              <div style="font-size:11px; color:#b0b8c8; font-weight:600; letter-spacing:0.5px; margin-bottom:10px;">对方气泡</div>
              <div style="display:flex; align-items:center; gap:8px;">
                <label style="position:relative; cursor:pointer;">
                  <div style="width:36px; height:36px; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.15); border:2px solid rgba(255,255,255,0.8);">
                    <input type="color" id="leftBubbleColor" value="#ffffff" onchange="document.getElementById(\'leftBubbleColorHex\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="width:56px;height:56px;border:none;cursor:pointer;padding:0;margin:-10px 0 0 -10px;opacity:1;">
                  </div>
                </label>
                <input type="text" id="leftBubbleColorHex" value="#ffffff" onchange="document.getElementById(\'leftBubbleColor\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="flex:1;height:34px;border:1.5px solid #ede8f5;border-radius:8px;padding:0 8px;font-size:12px;outline:none;font-family:monospace;color:#555;" placeholder="#HEX">
              </div>
            </div>
            <!-- 我的气泡颜色 -->
            <div style="background:#fff; border-radius:14px; padding:14px; box-shadow:0 2px 10px rgba(0,0,0,0.06);">
              <div style="font-size:11px; color:#b0b8c8; font-weight:600; letter-spacing:0.5px; margin-bottom:10px;">我的气泡</div>
              <div style="display:flex; align-items:center; gap:8px;">
                <label style="position:relative; cursor:pointer;">
                  <div style="width:36px; height:36px; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.15); border:2px solid rgba(255,255,255,0.8);">
                    <input type="color" id="rightBubbleColor" value="#f0b8c8" onchange="document.getElementById(\'rightBubbleColorHex\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="width:56px;height:56px;border:none;cursor:pointer;padding:0;margin:-10px 0 0 -10px;opacity:1;">
                  </div>
                </label>
                <input type="text" id="rightBubbleColorHex" value="#f0b8c8" onchange="document.getElementById(\'rightBubbleColor\').value=this.value; applyBubbleSettings(); updateBubblePreview();" style="flex:1;height:34px;border:1.5px solid #ede8f5;border-radius:8px;padding:0 8px;font-size:12px;outline:none;font-family:monospace;color:#555;" placeholder="#HEX">
              </div>
            </div>
          </div>

          <!-- 圆角 & 透明度 -->
          <div style="background:#fff; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,0.06); margin-bottom:18px; display:flex; flex-direction:column; gap:14px;">
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:12px; color:#888; font-weight:600;">气泡圆角</span>
                <span style="font-size:12px; color:#c084d8; font-weight:700; min-width:40px; text-align:right;"><span id="bubbleRadiusValue">12</span> px</span>
              </div>
              <input type="range" id="bubbleRadius" min="0" max="30" step="1" value="12" oninput="applyBubbleSettings(); updateBubblePreview();" style="width:100%; accent-color:#c084d8;">
            </div>
            <div style="height:1px; background:#f0eaf8; margin:0 -4px;"></div>
            <div>
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <span style="font-size:12px; color:#888; font-weight:600;">透明度</span>
                <span style="font-size:12px; color:#c084d8; font-weight:700; min-width:40px; text-align:right;"><span id="bubbleOpacityValue">1.0</span></span>
              </div>
              <input type="range" id="bubbleOpacity" min="0.1" max="1" step="0.1" value="1.0" oninput="applyBubbleSettings(); updateBubblePreview();" style="width:100%; accent-color:#c084d8;">
            </div>
          </div>

          <!-- 对方气泡装饰 -->
          <div style="background:#fff; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,0.06); margin-bottom:14px;">
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:14px;">
              <div style="width:3px; height:14px; background:linear-gradient(to bottom,#c084d8,#f0b8c8); border-radius:2px;"></div>
              <span style="font-size:13px; color:#555; font-weight:700;">对方气泡装饰</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
              <div id="leftDecPreview" style="width:44px; height:44px; border:2px dashed #e0d5f0; border-radius:10px; background-size:contain; background-repeat:no-repeat; background-position:center; flex-shrink:0; background-color:#faf8ff;"></div>
              <div style="display:flex; flex-direction:column; gap:6px; flex:1;">
                <div style="display:flex; gap:6px;">
                  <label style="flex:1; text-align:center; background:linear-gradient(135deg,#e8d5f8,#f8e8f5); color:#9b59b6; border-radius:8px; padding:7px 0; font-size:12px; font-weight:600; cursor:pointer; border:none;">上传<input type="file" accept="image/png" onchange="uploadBubbleDec(this, \'left\')" style="display:none;"></label>
                  <button style="flex:1; background:#f5f5f5; color:#999; border-radius:8px; padding:7px 0; font-size:12px; font-weight:600; border:none; cursor:pointer;" onclick="clearBubbleDec(\'left\')">清除</button>
                </div>
                <select id="leftDecCorner" onchange="applyBubbleDecSettings()" style="width:100%; padding:6px 10px; border:1.5px solid #ede8f5; border-radius:8px; font-size:12px; color:#666; outline:none; background:#fafafa;">
                  <option value="top-left">📍 左上角</option>
                  <option value="top-right">📍 右上角</option>
                  <option value="bottom-left">📍 左下角</option>
                  <option value="bottom-right">📍 右下角</option>
                </select>
              </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:12px;">
              <div>
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                  <span style="font-size:11px; color:#aaa; font-weight:600;">大小</span>
                  <span style="font-size:11px; color:#c084d8; font-weight:700;"><span id="leftDecSizeValue">30</span> px</span>
                </div>
                <input type="range" id="leftDecSize" min="10" max="100" step="1" value="30" oninput="applyBubbleDecSettings()" style="width:100%; accent-color:#c084d8;">
              </div>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div>
                  <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-size:11px; color:#aaa; font-weight:600;">垂直偏移</span>
                    <span style="font-size:11px; color:#c084d8; font-weight:700;"><span id="leftDecYValue">-10</span></span>
                  </div>
                  <input type="range" id="leftDecY" min="-15" max="15" step="1" value="-10" oninput="applyBubbleDecSettings()" style="width:100%; accent-color:#c084d8;">
                </div>
                <div>
                  <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-size:11px; color:#aaa; font-weight:600;">水平偏移</span>
                    <span style="font-size:11px; color:#c084d8; font-weight:700;"><span id="leftDecXValue">-5</span></span>
                  </div>
                  <input type="range" id="leftDecX" min="-15" max="15" step="1" value="-5" oninput="applyBubbleDecSettings()" style="width:100%; accent-color:#c084d8;">
                </div>
              </div>
            </div>
          </div>

          <!-- 我的气泡装饰 -->
          <div style="background:#fff; border-radius:14px; padding:16px; box-shadow:0 2px 10px rgba(0,0,0,0.06);">
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:14px;">
              <div style="width:3px; height:14px; background:linear-gradient(to bottom,#f0b8c8,#f7cfe8); border-radius:2px;"></div>
              <span style="font-size:13px; color:#555; font-weight:700;">我的气泡装饰</span>
            </div>
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
              <div id="rightDecPreview" style="width:44px; height:44px; border:2px dashed #fad5e5; border-radius:10px; background-size:contain; background-repeat:no-repeat; background-position:center; flex-shrink:0; background-color:#fff8fa;"></div>
              <div style="display:flex; flex-direction:column; gap:6px; flex:1;">
                <div style="display:flex; gap:6px;">
                  <label style="flex:1; text-align:center; background:linear-gradient(135deg,#fde8f0,#fce4ec); color:#e0748a; border-radius:8px; padding:7px 0; font-size:12px; font-weight:600; cursor:pointer; border:none;">上传<input type="file" accept="image/png" onchange="uploadBubbleDec(this, \'right\')" style="display:none;"></label>
                  <button style="flex:1; background:#f5f5f5; color:#999; border-radius:8px; padding:7px 0; font-size:12px; font-weight:600; border:none; cursor:pointer;" onclick="clearBubbleDec(\'right\')">清除</button>
                </div>
                <select id="rightDecCorner" onchange="applyBubbleDecSettings()" style="width:100%; padding:6px 10px; border:1.5px solid #fce4ec; border-radius:8px; font-size:12px; color:#666; outline:none; background:#fff8fa;">
                  <option value="top-left">📍 左上角</option>
                  <option value="top-right" selected>📍 右上角</option>
                  <option value="bottom-left">📍 左下角</option>
                  <option value="bottom-right">📍 右下角</option>
                </select>
              </div>
            </div>
            <div style="display:flex; flex-direction:column; gap:12px;">
              <div>
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                  <span style="font-size:11px; color:#aaa; font-weight:600;">大小</span>
                  <span style="font-size:11px; color:#e0748a; font-weight:700;"><span id="rightDecSizeValue">30</span> px</span>
                </div>
                <input type="range" id="rightDecSize" min="10" max="100" step="1" value="30" oninput="applyBubbleDecSettings()" style="width:100%; accent-color:#e0748a;">
              </div>
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
                <div>
                  <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-size:11px; color:#aaa; font-weight:600;">垂直偏移</span>
                    <span style="font-size:11px; color:#e0748a; font-weight:700;"><span id="rightDecYValue">-10</span></span>
                  </div>
                  <input type="range" id="rightDecY" min="-15" max="15" step="1" value="-10" oninput="applyBubbleDecSettings()" style="width:100%; accent-color:#e0748a;">
                </div>
                <div>
                  <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span style="font-size:11px; color:#aaa; font-weight:600;">水平偏移</span>
                    <span style="font-size:11px; color:#e0748a; font-weight:700;"><span id="rightDecXValue">-10</span></span>
                  </div>
                  <input type="range" id="rightDecX" min="-15" max="15" step="1" value="-10" oninput="applyBubbleDecSettings()" style="width:100%; accent-color:#e0748a;">
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>'''

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: replaced bubble UI")
else:
    print("ERROR: old block not found, check encoding or whitespace")
