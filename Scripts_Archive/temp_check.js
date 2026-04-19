const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf8');

// 1. worldbook
const wbIdx = content.indexOf('function renderWorldBookList');
if (wbIdx !== -1) {
    console.log('--- renderWorldBookList ---');
    console.log(content.substring(wbIdx, wbIdx + 1500));
}

// 2. load/import memory that might deform queue
const loadIdx = content.indexOf('function loadMemory');
if (loadIdx !== -1) {
    console.log('--- loadMemory ---');
    console.log(content.substring(loadIdx, loadIdx + 1500));
}

const sysIdx = content.indexOf('function buildSystemPrompt');
if (sysIdx !== -1) {
    console.log('--- buildSystemPrompt ---');
    console.log(content.substring(sysIdx, sysIdx + 1000));
}

const wsIdx = content.indexOf('function applyWritingStyle');
if (wsIdx !== -1) {
    console.log('--- applyWritingStyle ---');
    console.log(content.substring(wsIdx, wsIdx + 800));
}

// 3. inner voice background in CSS
try {
    const cssContent = fs.readFileSync('css/chat.css', 'utf8');
    const ivIdx = cssContent.indexOf('.inner-voice');
    if (ivIdx !== -1) {
        console.log('--- css/chat.css .inner-voice ---');
        console.log(cssContent.substring(ivIdx, ivIdx + 1000));
    }
} catch(e) {}
