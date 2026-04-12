// 兜底：无论Bmob是否加载成功，4秒后强制移除遮罩
setTimeout(function(){var m=document.getElementById('app-loading-mask');if(m&&m.style.display!='none'){m.style.display='none';var a=document.getElementById('activation-page');var sp=document.getElementById('splash-page');if(a&&(!a.style.display||a.style.display=='none')&&(!sp||!sp.style.display||sp.style.display=='none')){if(localStorage.getItem('OHO_ACTIVATED')==='true'){if(sp)sp.style.display='flex';}else{a.style.display='flex';}}}},4000);

// Bmob 初始化
Bmob.initialize("373cc21c1e33386c", "vanes13674535005");

document.addEventListener('DOMContentLoaded', () => {
  const activationPage = document.getElementById('activation-page');
  const splashPage = document.getElementById('splash-page');
  const appLoadingMask = document.getElementById('app-loading-mask');
  const activationBtn = document.getElementById('activation-btn');
  const qqInput = document.getElementById('activation-qq');
  const codeInput = document.getElementById('activation-code');

  // 检查是否已激活
  const isActivated = localStorage.getItem('OHO_ACTIVATED') === 'true';

  if (isActivated) {
    // 已激活，显示过渡动画
    splashPage.style.display = 'flex';
    appLoadingMask.style.display = 'none';
    
    // 2秒后隐藏过渡动画，进入主界面
    setTimeout(() => {
      splashPage.style.opacity = '0';
      setTimeout(() => {
        splashPage.style.display = 'none';
      }, 400);
    }, 2000);
  } else {
    // 未激活，显示激活页面
    activationPage.style.display = 'flex';
    appLoadingMask.style.display = 'none';
  }

  // 激活按钮点击事件
  activationBtn.addEventListener('click', async () => {
    const qq = qqInput.value.trim();
    const code = codeInput.value.trim();

    if (!qq || !code) {
      alert('请输入QQ号和验证码');
      return;
    }

    activationBtn.disabled = true;
    activationBtn.textContent = '验证中...';

    try {
      // 查询 Bmob 数据库中的激活码
      const query = Bmob.Query('activation_code');
      query.equalTo('qq', '==', qq);
      query.equalTo('code', '==', code);
      const results = await query.find();

      if (results.length === 0) {
        alert('QQ号或验证码错误');
        activationBtn.disabled = false;
        activationBtn.textContent = '激活进入';
        return;
      }

      const record = results[0];

      if (record.isUsed) {
        alert('该验证码已被使用，无法再次激活');
        activationBtn.disabled = false;
        activationBtn.textContent = '激活进入';
        return;
      }

      // 验证成功，更新数据库状态为已使用
      const updateQuery = Bmob.Query('activation_code');
      updateQuery.set('id', record.objectId);
      updateQuery.set('isUsed', true);
      await updateQuery.save();

      // 本地记录激活状态
      localStorage.setItem('OHO_ACTIVATED', 'true');

      // 隐藏激活页面，显示过渡动画
      activationPage.style.opacity = '0';
      setTimeout(() => {
        activationPage.style.display = 'none';
        splashPage.style.display = 'flex';
        splashPage.style.opacity = '1';
        
        // 2秒后隐藏过渡动画，进入主界面
        setTimeout(() => {
          splashPage.style.opacity = '0';
          setTimeout(() => {
            splashPage.style.display = 'none';
          }, 400);
        }, 2000);
      }, 400);

    } catch (error) {
      console.error('激活验证失败:', error);
      alert('网络错误，请稍后再试');
      activationBtn.disabled = false;
      activationBtn.textContent = '激活进入';
    }
  });
});
