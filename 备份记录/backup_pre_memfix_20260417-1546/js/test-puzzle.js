const thoughts = [
    "其实...刚才不该跟你吵的。\n看到你生气的样子，我心里也很难受。\n如果我先道歉，你会不会开心一点？",
    "你总是这么笨，连照顾自己都不会。\n可是...我就是喜欢这样的你。\n真拿你没办法。",
    "今天看到你对别人笑，我竟然有点嫉妒。\n我是不是太贪心了？\n好想把你藏起来，只属于我一个人。",
    "对不起，我刚才说话重了。\n我只是太在意你了，所以才会失控。\n原谅我好吗？"
];

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
            startY: 135,
            lineHeight: 32,
            maxWidth: 190,
            rotation: 0,
            fontSize: 24
        }
    },
    elite: {
        bg: 'ICON/paper_elite.jpg',
        font: "'EliteFont', 'Kaiti', serif",
        color: '#f8f8f8',
        textShadow: '1px 1px 2px rgba(0,0,0,0.8)',
        btnTextColor: '#f8f8f8',
        btnSaveUnderline: '#f8f8f8',
        btnDestroyUnderline: '#f8f8f8',
        textConfig: {
            startX: 50,
            startY: 215,
            lineHeight: 28,
            maxWidth: 200,
            rotation: 0,
            fontSize: 22
        }
    },
    student: {
        bg: 'ICON/paper_student.jpg',
        font: "'StudentFont', 'Kaiti', serif",
        color: '#1a53ff',
        textShadow: '1px 1px 0px rgba(255,255,255,0.5)',
        btnTextColor: '#1a53ff',
        btnSaveUnderline: '#1a53ff',
        btnDestroyUnderline: '#1a53ff',
        textConfig: {
            startX: 50,
            startY: 150,
            lineHeight: 30,
            maxWidth: 200,
            rotation: 0,
            fontSize: 20
        }
    }
};

let currentText = "";
let canvasDataUrl = "";
let currentPersona = "default";

function triggerEvent() {
    document.getElementById('triggerIcon').style.display = 'block';
}

async function openPuzzle() {
    currentPersona = document.getElementById('personaSelect').value;
    const config = personaConfig[currentPersona];
    
    document.getElementById('triggerIcon').style.display = 'none';
    document.getElementById('puzzleModal').classList.add('show');
    document.getElementById('puzzleContainer').style.display = 'block';
    document.getElementById('completePaper').classList.remove('show');
    document.getElementById('completePaper').classList.remove('destroy-anim');
    
    // 应用人设样式到完整纸条
    const paper = document.getElementById('completePaper');
    paper.style.backgroundImage = `url(${config.bg})`;
    const paperText = document.getElementById('paperText');
    paperText.style.fontFamily = config.font;
    paperText.style.color = config.color;
    paperText.style.textShadow = config.textShadow || 'none';
    paperText.style.fontSize = (config.textConfig.fontSize || 24) + 'px';
    
    // 应用旋转
    if (config.textConfig && config.textConfig.rotation) {
        paperText.style.transform = `rotate(${config.textConfig.rotation}deg)`;
    } else {
        paperText.style.transform = 'none';
    }
    
    // 更新按钮样式
    const styleId = 'dynamic-btn-style';
    let styleEl = document.getElementById(styleId);
    if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = styleId;
        document.head.appendChild(styleEl);
    }
    styleEl.innerHTML = `
        .btn-save { color: ${config.btnTextColor} !important; }
        .btn-save::after { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 15" preserveAspectRatio="none"><path d="M5,5 Q25,2 50,6 T95,4 M10,10 Q30,13 60,9 T85,11" stroke="${encodeURIComponent(config.btnSaveUnderline)}" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>') !important; }
        .btn-destroy { color: ${config.btnTextColor} !important; }
        .btn-destroy::after { background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 15" preserveAspectRatio="none"><path d="M5,5 Q25,2 50,6 T95,4 M10,10 Q30,13 60,9 T85,11" stroke="${encodeURIComponent(config.btnDestroyUnderline)}" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>') !important; }
    `;

    currentText = thoughts[Math.floor(Math.random() * thoughts.length)];
    
    // 确保字体加载
    try {
        await document.fonts.ready;
        const fontName = config.font.split(',')[0].replace(/'/g, '');
        await document.fonts.load(`${config.textConfig.fontSize || 24}px ${fontName}`);
        // 再次确认加载
        if (!document.fonts.check(`${config.textConfig.fontSize || 24}px ${fontName}`)) {
            console.warn("Font not loaded yet, waiting...");
            await new Promise(r => setTimeout(r, 500));
        }
    } catch(e) {
        console.error("Font loading error:", e);
    }
    
    initPuzzle(currentText, config);
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
    
    // 1. 渲染完整纸条
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    
    // 加载背景图
    const bgImg = new Image();
    bgImg.src = config.bg;
    await new Promise((resolve) => {
        bgImg.onload = resolve;
        bgImg.onerror = () => {
            console.error("Failed to load image:", config.bg);
            resolve(); 
        };
    });
    
    try {
        ctx.drawImage(bgImg, 0, 0, width, height);
    } catch(e) {
        console.error("Draw image failed", e);
        ctx.fillStyle = "#fffaf0";
        ctx.fillRect(0, 0, width, height);
    }
    
    // 绘制文字
    const fontSize = config.textConfig.fontSize || 24;
    ctx.font = `${fontSize}px ${config.font}`;
    ctx.fillStyle = config.color;
    ctx.textBaseline = 'top';
    
    const chars = text.split('');
    let curY = config.textConfig.startY;
    let displayLines = [];
    let currentLine = "";
    
    for (let i = 0; i < chars.length; i++) {
        let char = chars[i];
        if (char === "\n") {
            if (currentLine) { displayLines.push(currentLine); currentLine = ""; }
            continue;
        }
        
        let testLine = currentLine + char;
        let metrics = ctx.measureText(testLine);
        
        if (metrics.width > config.textConfig.maxWidth && currentLine !== "") {
            displayLines.push(currentLine);
            currentLine = char;
        } else {
            currentLine = testLine;
        }
    }
    if (currentLine) displayLines.push(currentLine);

    ctx.save();
    if (config.textConfig.rotation) {
        // 旋转中心改为文字起始区域
        ctx.translate(config.textConfig.startX, config.textConfig.startY);
        ctx.rotate(config.textConfig.rotation * Math.PI / 180);
        ctx.translate(-config.textConfig.startX, -config.textConfig.startY);
    }

    displayLines.forEach(line => {
        if (curY > height - 50) return;
        let offsetX = config.textConfig.startX;
        ctx.fillText(line, offsetX, curY);
        
        let div = document.createElement('div');
        div.style.position = 'absolute';
        div.style.left = offsetX + 'px';
        div.style.top = curY + 'px';
        div.style.fontFamily = config.font;
        div.style.color = config.color;
        div.style.textShadow = config.textShadow || 'none';
        div.textContent = line;
        document.getElementById('paperText').appendChild(div);
        curY += config.textConfig.lineHeight; 
    });
    ctx.restore();
    
    try {
        canvasDataUrl = canvas.toDataURL('image/png');
    } catch (e) {
        console.warn("toDataURL failed (likely file:// protocol CORS issue).", e);
        canvasDataUrl = null;
    }
    
    // 2. 乱序撕裂算法 (3-2-4)
    const rowConfigs = [3, 2, 4]; 
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
            
            pCtx.strokeStyle = 'rgba(0,0,0,0.1)';
            pCtx.lineWidth = 1;
            pCtx.stroke();
            
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

function saveThought() {
    if (!canvasDataUrl) {
        alert('由于浏览器本地文件安全限制（跨域），无法生成图片。请使用本地服务器（如 VS Code 的 Live Server）运行此页面。');
        return;
    }
    const album = document.getElementById('album');
    const img = document.createElement('img');
    img.src = canvasDataUrl;
    album.insertBefore(img, album.firstChild);
    document.getElementById('puzzleModal').classList.remove('show');
    alert('已保存到相册！');
}

function destroyThought() {
    const paper = document.getElementById('completePaper');
    paper.classList.add('destroy-anim');
    setTimeout(() => {
        document.getElementById('puzzleModal').classList.remove('show');
        paper.classList.remove('destroy-anim');
        paper.classList.remove('show');
    }, 1800);
}
