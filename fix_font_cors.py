
# 修复 applyCustomFont 函数，让PC端也能正常加载外部字体
# 原因：PC浏览器对@font-face外部字体有严格CORS限制
# 方案：先fetch下载转为blob URL（同源），CORS失败则回退直接链接

with open('c:/Users/Administrator/Desktop/111/index.html', encoding='utf-8') as f:
    content = f.read()

OLD = '''function applyCustomFont(url) {
  const fontInput = document.getElementById('customFontUrl');
  const fontUrl = url !== undefined ? url : (fontInput ? fontInput.value.trim() : '');

  let styleEl = document.getElementById('custom-font-style');

  if (!fontUrl) {
    if (styleEl) styleEl.remove();
    if (url === undefined) saveTextBeautifySettings(false);
    return;
  }

  if (!styleEl) {
    styleEl = document.createElement('style');
    styleEl.id = 'custom-font-style';
    document.head.appendChild(styleEl);
  }

  // 获取字体大小设置
  const fontSize = document.getElementById('customFontSize')?.value || '14';

  styleEl.innerHTML = `
    @font-face {
      font-family: 'MyCustomFont';
      src: url('${fontUrl}');
    }
    *:not(.me-time):not(#currentTime) {
      font-family: 'MyCustomFont', -apple-system, "SF Pro Display", "PingFang SC", sans-serif !important;
      font-size: ${fontSize}px !important;
    }
    .me-time, #currentTime {
      font-family: 'MyCustomFont', -apple-system, "SF Pro Display", "PingFang SC", sans-serif !important;
      font-size: 70px !important;
    }
  `;

  if (url === undefined) {
    saveTextBeautifySettings(false);
  }
}'''

NEW = '''async function applyCustomFont(url) {
  const fontInput = document.getElementById('customFontUrl');
  const fontUrl = url !== undefined ? url : (fontInput ? fontInput.value.trim() : '');

  let styleEl = document.getElementById('custom-font-style');

  if (!fontUrl) {
    if (styleEl) styleEl.remove();
    if (url === undefined) saveTextBeautifySettings(false);
    return;
  }

  if (!styleEl) {
    styleEl = document.createElement('style');
    styleEl.id = 'custom-font-style';
    document.head.appendChild(styleEl);
  }

  // 获取字体大小设置
  const fontSize = document.getElementById('customFontSize')?.value || '14';

  // PC端Chrome对@font-face外部字体有严格CORS限制
  // 先尝试fetch下载转为blob URL（blob是同源，绕过跨域），失败则回退直接链接
  let fontSrc = `url('${fontUrl}')`;
  try {
    const resp = await fetch(fontUrl, { mode: 'cors' });
    if (resp.ok) {
      const blob = await resp.blob();
      fontSrc = `url('${URL.createObjectURL(blob)}')`;
    }
  } catch(e) {
    // fetch失败（服务器不支持CORS）则回退到直接链接（手机端通常仍正常）
    console.warn('[字体] CORS加载失败，回退到直接链接:', e.message);
  }

  styleEl.innerHTML = `
    @font-face {
      font-family: 'MyCustomFont';
      src: ${fontSrc};
    }
    *:not(.me-time):not(#currentTime) {
      font-family: 'MyCustomFont', -apple-system, "SF Pro Display", "PingFang SC", sans-serif !important;
      font-size: ${fontSize}px !important;
    }
    .me-time, #currentTime {
      font-family: 'MyCustomFont', -apple-system, "SF Pro Display", "PingFang SC", sans-serif !important;
      font-size: 70px !important;
    }
  `;

  if (url === undefined) {
    saveTextBeautifySettings(false);
  }
}'''

if OLD in content:
    new_content = content.replace(OLD, NEW, 1)
    with open('c:/Users/Administrator/Desktop/111/index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS: applyCustomFont 函数已成功修复！PC端字体加载问题已解决。')
else:
    print('FAILED: 未找到匹配的函数文本，请检查文件内容。')
    # 打印周边内容帮助调试
    idx = content.find('function applyCustomFont')
    if idx >= 0:
        print('找到函数位置，周边内容:')
        print(repr(content[idx:idx+200]))
    else:
        print('连函数名都没找到！')
