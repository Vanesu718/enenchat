document.addEventListener('DOMContentLoaded', () => {
    const triggerBtn = document.getElementById('trigger-thought-btn');
    const crumpledPaper = document.getElementById('crumpled-paper');
    const modal = document.getElementById('thought-modal');
    const thoughtContent = document.getElementById('thought-content');
    const saveBtn = document.getElementById('save-btn');
    const destroyBtn = document.getElementById('destroy-btn');
    const album = document.getElementById('couple-album');
    // 模拟的内心独白
    const secretThoughts = [
        "其实...刚才不该跟你吵的。",
        "如果我先道歉，你会不会开心一点？",
        "算了，还是我错了。",
        "好想抱抱你啊...",
    ];

    // 1. 自动触发事件 (页面加载3秒后)
    setTimeout(() => {
        crumpledPaper.classList.add('show');
    }, 3000);

    // 2. 点击纸团，展开纸条 (纯 CSS 动画)
    crumpledPaper.addEventListener('click', () => {
        crumpledPaper.classList.remove('show'); // 点击后纸团消失
        
        // 随机选择一条心事
        const thought = secretThoughts[Math.floor(Math.random() * secretThoughts.length)];
        
        // 自然排版，每行2-4个字
        thoughtContent.innerHTML = ''; // 清空
        let tempLine = '';
        for (let i = 0; i < thought.length; i++) {
            tempLine += thought[i];
            if (tempLine.length >= 2 && (Math.random() > 0.3 || tempLine.length === 4)) {
                const span = document.createElement('span');
                span.textContent = tempLine;
                thoughtContent.appendChild(span);
                tempLine = '';
            }
        }
        if (tempLine) {
            const span = document.createElement('span');
            span.textContent = tempLine;
            thoughtContent.appendChild(span);
        }

        // 确保移除之前的动画类
        const paperSheet = modal.querySelector('.thought-paper');
        paperSheet.classList.remove('scribble', 'fade-out');
        
        modal.classList.add('show');
    });

    // 3. 点击销毁 (划掉特效)
    destroyBtn.addEventListener('click', () => {
        const paperSheet = modal.querySelector('.thought-paper');
        
        // 触发划掉动画
        paperSheet.classList.add('scribble');
        
        // 模拟AI不知道
        console.log("【模拟】AI对此事毫不知情。");

        // 等待划掉动画完成 (最长延迟 0.7s + 动画 0.8s = 1.5s)
        setTimeout(() => {
            // 触发纸张消失动画
            paperSheet.classList.add('fade-out');
            
            // 等待消失动画完成
            setTimeout(() => {
                modal.classList.remove('show');
                paperSheet.classList.remove('scribble', 'fade-out');
            }, 500);
        }, 1500);
    });

    // 4. 点击保存
    saveBtn.addEventListener('click', () => {
        // 模拟AI知道
        console.log("【模拟】AI已获知你保存了纸条，并会记住这件事。");
        
        // 使用canvas将文字转为图片
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // 设置canvas尺寸和样式
        canvas.width = 400;
        canvas.height = 300;
        
        // 绘制背景
        ctx.fillStyle = '#fffaf0';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // 绘制网格线
        ctx.strokeStyle = 'rgba(211, 211, 211, 0.5)';
        ctx.lineWidth = 1;
        for (let i = 20; i < canvas.width; i += 20) {
            ctx.beginPath();
            ctx.moveTo(i, 0);
            ctx.lineTo(i, canvas.height);
            ctx.stroke();
        }
        for (let i = 20; i < canvas.height; i += 20) {
            ctx.beginPath();
            ctx.moveTo(0, i);
            ctx.lineTo(canvas.width, i);
            ctx.stroke();
        }

        // 绘制文字
        ctx.font = "30px 'Handwritten', cursive";
        ctx.fillStyle = '#333';
        ctx.textAlign = 'center';
        
        // 保存上下文，应用旋转
        ctx.save();
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(-5 * Math.PI / 180);

        const lines = Array.from(thoughtContent.querySelectorAll('span')).map(span => span.textContent);
        const lineHeight = 50;
        const startY = -((lines.length - 1) * lineHeight) / 2;

        lines.forEach((line, index) => {
            ctx.fillText(line, 0, startY + index * lineHeight);
        });

        // 恢复上下文
        ctx.restore();

        // 创建图片并添加到相册
        const img = new Image();
        img.src = canvas.toDataURL('image/png');
        
        if (album.querySelector('p')) {
            album.innerHTML = ''; // 清除初始提示
        }
        album.appendChild(img);

        // 关闭模态框
        modal.classList.remove('show');
    });

});
