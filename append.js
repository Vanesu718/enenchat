// ========== 朋友圈及论坛面具选择功能 ==========
function togglePostMomentMaskSelect() {
  const select = document.getElementById('postMomentMaskSelect');
  if (select) {
    select.style.display = select.style.display === 'block' ? 'none' : 'block';
  }
}

function updatePostMomentMaskIcon() {
  const select = document.getElementById('postMomentMaskSelect');
  const icon = document.getElementById('postMomentMaskIcon');
  if (select && icon) {
    const selectedId = select.value;
    if (selectedId) {
      const mask = userMasks.find(m => m.id === selectedId);
      if (mask && mask.avatar) {
        icon.src = mask.avatar;
        icon.style.borderRadius = '50%';
        icon.style.objectFit = 'cover';
      } else {
        icon.src = 'ICON/论坛面具图标.png';
        icon.style.borderRadius = '0';
      }
    } else {
      icon.src = 'ICON/论坛面具图标.png';
      icon.style.borderRadius = '0';
    }
    // 选择后自动收起
    select.style.display = 'none';
  }
}

function toggleForumCommentMaskSelect() {
  const select = document.getElementById('forumCommentMaskSelect');
  if (select) {
    select.style.display = select.style.display === 'block' ? 'none' : 'block';
  }
}

function updateForumMaskIcon() {
  const select = document.getElementById('forumCommentMaskSelect');
  const icon = document.getElementById('forumCommentMaskIcon');
  if (select && icon) {
    const selectedId = select.value;
    if (selectedId) {
      const mask = userMasks.find(m => m.id === selectedId);
      if (mask && mask.avatar) {
        icon.src = mask.avatar;
        icon.style.borderRadius = '50%';
        icon.style.objectFit = 'cover';
      } else {
        icon.src = 'ICON/论坛面具图标.png';
        icon.style.borderRadius = '0';
      }
    } else {
      icon.src = 'ICON/论坛面具图标.png';
      icon.style.borderRadius = '0';
    }
    // 选择后自动收起
    select.style.display = 'none';
  }
}

// 点击空白处收起下拉菜单
document.addEventListener('click', function(e) {
  const postSelect = document.getElementById('postMomentMaskSelect');
  const postIcon = document.getElementById('postMomentMaskIcon');
  if (postSelect && postSelect.style.display === 'block') {
    if (e.target !== postSelect && e.target !== postIcon) {
      postSelect.style.display = 'none';
    }
  }

  const forumSelect = document.getElementById('forumCommentMaskSelect');
  const forumIcon = document.getElementById('forumCommentMaskIcon');
  if (forumSelect && forumSelect.style.display === 'block') {
    if (e.target !== forumSelect && e.target !== forumIcon) {
      forumSelect.style.display = 'none';
    }
  }
});