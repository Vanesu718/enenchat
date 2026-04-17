
const personaConfig = {
    default: {
        bg: 'ICON/paper_default.png',
        font: "'Handwritten', 'Kaiti', serif",
        color: '#222',
        textShadow: '1px 1px 0px rgba(255,255,255,0.5)',
        btnTextColor: '#333',
        btnSaveUnderline: '#333',
        btnDestroyUnderline: '#333',
        textConfig: {
            startX: 55,
            startY: 110,
            lineHeight: 32,
            maxWidth: 210,
            rotation: 0,
            fontSize: 32
        }
    }
};

let currentSecretThought = "";
let canvasDataUrl = "";
let currentPersonaType = "default";

function triggerSecretThought(thought, personaType = 'default') {
    currentSecretThought = thought;
    currentPersonaType = personaType;
    document.getElementById('triggerIcon').style.display = 'block';
}

async function openPuzzle() {
    const config = personaConfig[currentPersonaType] || personaConfig.default;
    
    document.getElementById('triggerIcon').style.display = 'none';
    document.getElementById('puzzleModal').classList.add('show');
    document.getElementById('puzzleContainer').style.display = 'block';
    document.getElementById('completePaper').classList.remove('show');
    document.getElementById('completePaper').classList.remove('destroy-anim');
    
    const paper = document.getElementById('completePaper');
    paper.style.backgroundImage = `url(${config.bg})`;
    const paperText = document.getElementById('paperText');
    paperText.style.fontFamily = config.font;
    paperText.style.color = config.color;
    paperText.style.textShadow = config.textShadow || 'none';
    paperText.style.setProperty('font-size', (config.textConfig.fontSize || 24) + 'px', 'important');
    
    if (config.textConfig && config.textConfig.rotation) {
        paperText.style.transform = `rotate(${config.textConfig.rotation}deg)`;
    } else {
        paperText.style.transform = 'none';
    }
    
    const styleId = 'dynamic-btn-style';
    let styleEl = document.getElementById(styleId);
    if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = styleId;
        document.head.appendChild(styleEl);
    }
    styleEl.innerHTML = `
        .btn-save { color: ${config.btnTextColor} !important; }
        .btn-destroy { color: ${config.btnTextColor} !important; }
    `;

    try {
        await document.fonts.ready;
        const fontName = config.font.split(',')[0].replace(/'/g, '');
        await document.fonts.load(`${config.textConfig.fontSize || 24}px ${fontName}`);
        if (!document.fonts.check(`${config.textConfig.fontSize || 24}px ${fontName}`)) {
            await new Promise(r => setTimeout(r, 500));
        }
    } catch(e) {
        console.error("Font loading error:", e);
    }
    
    initPuzzle(currentSecretThought, config);
}

function generateJaggedPath(p1, p2, segments = 15, variance = 8) {
    const path = [p1];
    for (let i = 1; i < segments; i++) {
        const t = i / segments;
        let x = p1.x + (p2.x - p1.x) * t;
        let y = p1.y + (p2.y - p1.y) * t;
        const angle = Math.atan2(p2.y - p1.y, p2.x - p1.x) + Math.PI / 2;
        const offset = (Math.random() - 0.5) * variance;
        x += Math.cos(angle) * offset;
        y += Math.sin(angle) * offset;
        path.push({ x, y });
    }
    path.push(p2);
    return path;
}

async function initPuzzle(text, config) {
    const container = document.getElementById('puzzleContainer');
    container.innerHTML = '';
    document.getElementById('paperText').innerHTML = '';
    
    const width = 300;
    const height = 400;
    
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    const bgImg = new Image();
    // 移除 crossOrigin 限制，避免本地 file:// 协议下报错
    // bgImg.crossOrigin = "Anonymous";
    
    // 尝试将图片转换为 base64 以避免跨域问题
    const loadImgAsBase64 = async (url) => {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onloadend = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });
        } catch (e) {
            console.warn("Failed to fetch image as blob, falling back to direct src", e);
            return url;
        }
    };

    bgImg.src = await loadImgAsBase64(config.bg);
    
    await new Promise((resolve) => {
        bgImg.onload = resolve;
        bgImg.onerror = () => {
            console.error("Failed to load image:", config.bg);
            resolve(); 
        };
    });
    
    try {
        // 模拟 background-size: cover 和 background-position: center
        const imgRatio = bgImg.width / bgImg.height;
        const canvasRatio = width / height;
        let drawWidth, drawHeight, drawX, drawY;

        if (imgRatio > canvasRatio) {
            // 图片比画布宽，以高度为准缩放，截取左右
            drawHeight = height;
            drawWidth = bgImg.width * (height / bgImg.height);
            drawX = (width - drawWidth) / 2;
            drawY = 0;
        } else {
            // 图片比画布高，以宽度为准缩放，截取上下
            drawWidth = width;
            drawHeight = bgImg.height * (width / bgImg.width);
            drawX = 0;
            drawY = (height - drawHeight) / 2;
        }
        ctx.drawImage(bgImg, drawX, drawY, drawWidth, drawHeight);
    } catch(e) {
        ctx.fillStyle = "#fffaf0";
        ctx.fillRect(0, 0, width, height);
    }
    
    const fontSize = config.textConfig.fontSize || 24;
    ctx.font = `${fontSize}px ${config.font}`;
    ctx.fillStyle = config.color;
    ctx.textBaseline = 'top';
    
    // 增加安全边距，防止文字出格
    const safePadding = 15;
    const safeMaxWidth = config.textConfig.maxWidth - safePadding * 2;
    
    // 处理 AI 返回的换行符（可能是真实的换行符，也可能是转义的 \n）
    const normalizedText = text.replace(/\\n/g, '\n');
    const paragraphs = normalizedText.split('\n');
    
    let curY = config.textConfig.startY;
    let displayLines = [];
    
    paragraphs.forEach(paragraph => {
        if (!paragraph) {
            // 空行保留，增加空气感
            displayLines.push("");
            return;
        }
        
        const chars = paragraph.split('');
        let currentLine = "";
        const punctuations = /^[，。！？、；：”’）】》\.\,\!\?\;\:\'\"\]\}\>\-—…~\s·•]/;
        
        for (let i = 0; i < chars.length; i++) {
            let char = chars[i];
            let testLine = currentLine + char;
            let metrics = ctx.measureText(testLine);
            
            if (metrics.width > safeMaxWidth && currentLine !== "") {
                if (punctuations.test(char)) {
                    currentLine += char;
                    // 继续向后检查，把连续的标点符号都加到当前行
                    while (i + 1 < chars.length && punctuations.test(chars[i + 1])) {
                        currentLine += chars[i + 1];
                        i++;
                    }
                    displayLines.push(currentLine);
                    currentLine = "";
                } else {
                    displayLines.push(currentLine);
                    currentLine = char;
                }
            } else {
                currentLine = testLine;
            }
        }
        if (currentLine) displayLines.push(currentLine);
    });

    ctx.save();
    if (config.textConfig.rotation) {
        ctx.translate(config.textConfig.startX, config.textConfig.startY);
        ctx.rotate(config.textConfig.rotation * Math.PI / 180);
        ctx.translate(-config.textConfig.startX, -config.textConfig.startY);
    }

    displayLines.forEach(line => {
        if (curY > height - 50) return;
        let offsetX = config.textConfig.startX + 15; // 加上 safePadding
        ctx.fillText(line, offsetX, curY);
        
        let div = document.createElement('div');
        div.style.position = 'absolute';
        div.style.left = offsetX + 'px';
        div.style.top = curY + 'px';
        div.style.fontFamily = config.font;
        div.style.color = config.color;
        div.style.textShadow = config.textShadow || 'none';
        div.style.setProperty('font-size', (config.textConfig.fontSize || 24) + 'px', 'important');
        div.textContent = line;
        document.getElementById('paperText').appendChild(div);
        curY += config.textConfig.lineHeight; 
    });
    ctx.restore();
    
    try {
        canvasDataUrl = canvas.toDataURL('image/png');
    } catch (e) {
        console.warn("toDataURL failed. This is expected on file:// protocol.", e);
        canvasDataUrl = null;
    }
    
    // 随机生成切割样式，例如 2-3-2, 3-3-3, 4-2-3 等
    const possibleRows = [2, 3, 4];
    const rowConfigs = [
        possibleRows[Math.floor(Math.random() * possibleRows.length)],
        possibleRows[Math.floor(Math.random() * possibleRows.length)],
        possibleRows[Math.floor(Math.random() * possibleRows.length)]
    ];
    const hPaths = []; 
    const vPaths = []; 
    
    for (let i = 0; i <= 3; i++) {
        const y = (i / 3) * height;
        const p1 = { x: 0, y: y };
        const p2 = { x: width, y: y };
        if (i === 0 || i === 3) {
            hPaths[i] = [p1, p2];
        } else {
            hPaths[i] = generateJaggedPath(p1, p2, 20, 10);
        }
    }
    
    for (let r = 0; r < 3; r++) {
        vPaths[r] = [];
        const numPieces = rowConfigs[r];
        for (let c = 0; c <= numPieces; c++) {
            const x = (c / numPieces) * width;
            const pTop = { x: x, y: (r / 3) * height };
            const pBottom = { x: x, y: ((r + 1) / 3) * height };
            
            if (c === 0 || c === numPieces) {
                vPaths[r][c] = [pTop, pBottom];
            } else {
                vPaths[r][c] = generateJaggedPath(pTop, pBottom, 15, 8);
            }
        }
    }
    
    for (let r = 0; r < 3; r++) {
        const numPieces = rowConfigs[r];
        for (let c = 0; c < numPieces; c++) {
            const pieceCanvas = document.createElement('canvas');
            const margin = 40;
            pieceCanvas.width = (width / numPieces) + margin * 2;
            pieceCanvas.height = (height / 3) + margin * 2;
            const pCtx = pieceCanvas.getContext('2d');
            
            const topPath = hPaths[r].filter(p => p.x >= (c/numPieces)*width - 1 && p.x <= ((c+1)/numPieces)*width + 1);
            const bottomPath = hPaths[r+1].filter(p => p.x >= (c/numPieces)*width - 1 && p.x <= ((c+1)/numPieces)*width + 1);
            const leftPath = vPaths[r][c];
            const rightPath = vPaths[r][c+1];
            
            const originX = (c / numPieces) * width;
            const originY = (r / 3) * height;
            
            pCtx.translate(margin - originX, margin - originY);
            pCtx.beginPath();
            
            pCtx.moveTo(leftPath[0].x, leftPath[0].y);
            topPath.forEach(p => pCtx.lineTo(p.x, p.y));
            rightPath.forEach(p => pCtx.lineTo(p.x, p.y));
            [...bottomPath].reverse().forEach(p => pCtx.lineTo(p.x, p.y));
            [...leftPath].reverse().forEach(p => pCtx.lineTo(p.x, p.y));
            
            pCtx.closePath();
            pCtx.save();
            pCtx.clip();
            pCtx.drawImage(canvas, 0, 0);
            pCtx.restore();
            
            // pCtx.strokeStyle = 'rgba(0,0,0,0.1)';
            // pCtx.lineWidth = 1;
            // pCtx.stroke();
            
            const pieceDiv = document.createElement('div');
            pieceDiv.className = 'puzzle-piece';
            pieceDiv.style.width = pieceCanvas.width + 'px';
            pieceDiv.style.height = pieceCanvas.height + 'px';
            
            pieceCanvas.style.width = '100%';
            pieceCanvas.style.height = '100%';
            pieceCanvas.style.pointerEvents = 'none';
            pieceDiv.appendChild(pieceCanvas);
            
            const rx = (Math.random() - 0.5) * 180;
            const ry = (Math.random() - 0.5) * 150 + 180;
            const rr = (Math.random() - 0.5) * 60;
            
            pieceDiv.style.left = (originX - margin + rx) + 'px';
            pieceDiv.style.top = (originY - margin + ry) + 'px';
            pieceDiv.style.transform = `rotate(${rr}deg)`;
            
            pieceDiv.dataset.correctX = originX - margin;
            pieceDiv.dataset.correctY = originY - margin;
            pieceDiv.dataset.snapped = "false";
            
            container.appendChild(pieceDiv);
            makeDraggable(pieceDiv, container);
        }
    }
}

function makeDraggable(el, container) {
    let isDragging = false;
    let startX, startY, initialLeft, initialTop;
    
    el.addEventListener('pointerdown', (e) => {
        if (el.dataset.snapped === "true") return;
        isDragging = true;
        el.setPointerCapture(e.pointerId);
        startX = e.clientX;
        startY = e.clientY;
        initialLeft = parseFloat(el.style.left);
        initialTop = parseFloat(el.style.top);
        el.style.transform = 'rotate(0deg) scale(1.1)';
        el.style.zIndex = 1000;
        el.style.filter = 'drop-shadow(5px 5px 15px rgba(0,0,0,0.4))';
    });
    
    el.addEventListener('pointermove', (e) => {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        el.style.left = (initialLeft + dx) + 'px';
        el.style.top = (initialTop + dy) + 'px';
    });
    
    el.addEventListener('pointerup', (e) => {
        if (!isDragging) return;
        isDragging = false;
        el.releasePointerCapture(e.pointerId);
        el.style.zIndex = 10;
        el.style.filter = 'drop-shadow(2px 2px 5px rgba(0,0,0,0.5))';
        
        const curX = parseFloat(el.style.left);
        const curY = parseFloat(el.style.top);
        const targetX = parseFloat(el.dataset.correctX);
        const targetY = parseFloat(el.dataset.correctY);
        
        const dist = Math.sqrt(Math.pow(curX - targetX, 2) + Math.pow(curY - targetY, 2));
        
        if (dist < 40) {
            el.style.left = targetX + 'px';
            el.style.top = targetY + 'px';
            el.style.transform = 'rotate(0deg) scale(1)';
            el.dataset.snapped = "true";
            el.classList.add('snapped');
            el.classList.add('flash-edge');
            setTimeout(() => el.classList.remove('flash-edge'), 600);
            checkWin();
        } else {
            el.style.transform = `rotate(${(Math.random()-0.5)*60}deg) scale(1)`;
        }
    });
}

function checkWin() {
    const pieces = document.querySelectorAll('.puzzle-piece');
    const all = Array.from(pieces).every(p => p.dataset.snapped === "true");
    if (all) {
        setTimeout(() => {
            document.getElementById('puzzleContainer').style.display = 'none';
            const paper = document.getElementById('completePaper');
            paper.classList.add('show');
        }, 800);
    }
}

async function saveThought() {
    if (!canvasDataUrl) {
        showToast('由于浏览器安全限制，无法生成图片。请在服务器环境中使用。');
        return;
    }
    
    if (!currentContactId) return;

    // 保存到情侣相册
    let album = await IndexedDBManager.getData(`COUPLE_ALBUM_${currentContactId}`);
    if (!album) {
        let oldAlbum = await getFromStorage(`COUPLE_ALBUM_${currentContactId}`);
        if (oldAlbum) {
            album = typeof oldAlbum === 'string' ? JSON.parse(oldAlbum) : oldAlbum;
        } else {
            album = [];
        }
    }
    
    if (!Array.isArray(album)) album = [];
    
    const imageId = `thought_${Date.now()}`;
    await IndexedDBManager.saveImage(imageId, canvasDataUrl, 'thought');
    
    album.unshift({
        id: Date.now(),
        srcId: imageId,
        description: '隐秘心事纸条',
        time: Date.now()
    });
    
    await IndexedDBManager.saveData(`COUPLE_ALBUM_${currentContactId}`, album);
    
    document.getElementById('puzzleModal').classList.remove('show');
    showToast('已保存到情侣相册！');

    // 注入记忆
    const memoryMessage = `[系统提示：用户发现了你的心声纸条并保存了下来，纸条内容是：“${currentSecretThought}”]`;
    
    if (!chatRecords[currentContactId]) {
        chatRecords[currentContactId] = [];
    }
    chatRecords[currentContactId].push({
        side: 'notif',
        type: 'rp_notif',
        content: `<div style="text-align:center;font-size:12px;color:#999;margin:10px 0;">${memoryMessage}</div>`,
        time: Date.now()
    });
    
    await saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords));
    
    // 如果当前在聊天页面，刷新UI
    if (document.getElementById('chat-win').classList.contains('show')) {
        renderChat();
    }
}

function destroyThought() {
    const paper = document.getElementById('completePaper');
    paper.classList.add('destroy-anim');
    setTimeout(() => {
        document.getElementById('puzzleModal').classList.remove('show');
        paper.classList.remove('destroy-anim');
        paper.classList.remove('show');
    }, 1800);
    // AI无感知
}

window.closePuzzleModal = function() {
    document.getElementById('puzzleModal').classList.remove('show');
    document.getElementById('puzzleContainer').style.display = 'none';
    document.getElementById('completePaper').classList.remove('show');
    document.getElementById('completePaper').classList.remove('destroy-anim');
}
