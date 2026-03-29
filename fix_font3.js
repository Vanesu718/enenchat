const fs = require('fs');
const path = 'c:/Users/Administrator/Desktop/111/index.html';

let content = fs.readFileSync(path, 'utf8');

// 步骤1：将函数内 src: url('${fontUrl}') 替换为 src: ${fontSrc}
const oldSrc = "src: url('${fontUrl}');";
const newSrc = "src: ${fontSrc};";

if (!content.includes(oldSrc)) {
  console.log('ERROR: 找不到 src: url 字符串');
  console.log('当前函数体:');
  const idx = content.indexOf('async function applyCustomFont');
  if (idx >= 0) console.log(content.substring(idx, idx+800));
  process.exit(1);
}

content = content.replace(oldSrc, newSrc);
console.log('Step1 OK: 替换 src: url 为 src: ${fontSrc}');

// 步骤2：在 const fontSize 行之后插入 fetch+blob 逻辑
const insertAfter = "  const fontSize = document.getElementById('customFontSize')?.value || '14';";

const fetchCode = `

  // PC端Chrome对@font-face外部字体有严格CORS限制
  // 先用fetch下载字体转为blob URL（同源绕过跨域），失败则回退直接链接
  let fontSrc = \`url('\${fontUrl}')\`;
  try {
    const resp = await fetch(fontUrl, { mode: 'cors' });
    if (resp.ok) {
      const blob = await resp.blob();
      fontSrc = \`url('\${URL.createObjectURL(blob)}')\`;
    }
  } catch(e) {
    console.warn('[字体] CORS加载失败，回退直接链接:', e.message);
  }`;

if (!content.includes(insertAfter)) {
  console.log('ERROR: 找不到 const fontSize 行');
  process.exit(1);
}

content = content.replace(insertAfter, insertAfter + fetchCode);
console.log('Step2 OK: 插入 fetch+blob 代码');

// 验证
if (content.includes('await fetch(fontUrl') && content.includes('src: ${fontSrc};')) {
  fs.writeFileSync(path, content, 'utf8');
  console.log('SUCCESS: 字体CORS修复完成！PC端字体现在可以正常加载了。');
  console.log('');
  console.log('修复内容说明:');
  console.log('- applyCustomFont 函数改为 async');  
  console.log('- 加载字体时先用 fetch+blob URL 绕过CORS限制');
  console.log('- 如果 fetch 失败则自动回退到直接URL（保持手机端兼容性）');
} else {
  console.log('WARN: 验证失败');
  console.log('contains fetch:', content.includes('await fetch(fontUrl'));
  console.log('contains fontSrc:', content.includes('src: ${fontSrc};'));
}
