const fs = require('fs');

let html = fs.readFileSync('index.html', 'utf8');

// Replace "语言规范" with "世界观" in worldbook tabs
html = html.replace(
  `<div class="wb-tab" onclick="filterWorldBook('语言规范')" data-category="语言规范" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">语言规范</div>`,
  `<div class="wb-tab" onclick="filterWorldBook('世界观')" data-category="世界观" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">世界观</div>\n        <div class="wb-tab" onclick="filterWorldBook('其他')" data-category="其他" style="flex:1; text-align:center; padding:8px; border-radius:8px; cursor:pointer; font-size:13px; background:#f5f5f5; color:var(--text-dark);">其他</div>`
);

// Replace in select options
html = html.replace(
  `<option value="语言规范">语言规范</option>`,
  `<option value="世界观">世界观</option>\n            <option value="其他">其他</option>`
);

fs.writeFileSync('index.html', html, 'utf8');
console.log('Categories updated in index.html');
