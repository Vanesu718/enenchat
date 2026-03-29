const fs = require('fs');

function updateIndexHtml() {
    let html = fs.readFileSync('index.html', 'utf-8');

    // Add forum menu item to discover page
    if (!html.includes('openSub(\'forum-page\')')) {
        html = html.replace(
            /<div class="menu-item" onclick="openSub\('moments-page'\)">朋友?\/?div>/g,
            '<div class="menu-item" onclick="openSub(\'moments-page\')">朋友圈</div>\n          <div class="menu-item" onclick="openSub(\'forum-page\')">论坛</div>'
        );
    }

    // Add forum page HTML
    const forumHtml = `
    <div class="sub-page" id="forum-page">
      <div class="page-header">
        <div class="page-back" onclick="closeSub('forum-page')"><svg viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg></div>
        <div class="page-title">论坛</div>
        <div class="page-actions" style="margin-left: auto; padding-right: 15px;">
          <button onclick="refreshForum()" style="background:none; border:none; color:var(--main-pink); font-size:14px; cursor:pointer;">刷新</button>
        </div>
      </div>
      <div class="forum-tabs" style="display: flex; background: rgba(255,255,255,0.8); border-bottom: 1px solid rgba(0,0,0,0.05);">
        <div class="forum-tab active" onclick="switchForumTab('gossip')" style="flex:1; text-align:center; padding:12px 0; font-size:14px; cursor:pointer; color:var(--main-pink); border-bottom:2px solid var(--main-pink); font-weight:bold;">八卦</div>
        <div class="forum-tab" onclick="switchForumTab('entertainment')" style="flex:1; text-align:center; padding:12px 0; font-size:14px; cursor:pointer; color:var(--text-light); border-bottom:2px solid transparent;">娱乐</div>
        <div class="forum-tab" onclick="switchForumTab('horror')" style="flex:1; text-align:center; padding:12px 0; font-size:14px; cursor:pointer; color:var(--text-light); border-bottom:2px solid transparent;">恐怖</div>
      </div>
      <div class="page-body" id="forum-content" style="padding: 10px; background: #f5f5f5; overflow-y: auto; height: calc(100% - 100px);">
        <!-- Posts will be generated here -->
      </div>
    </div>
    `;
    
    if (!html.includes('id="forum-page"')) {
        html = html.replace('<!-- 朋友圈二级页?-->', '<!-- 论坛二级页 -->\n' + forumHtml + '\n      <!-- 朋友圈二级页?-->');
    }

    // Add forum JS logic
    const forumJs = `
// ==================== 论坛功能 ====================
let currentForumTab = 'gossip';

const forumData = {
  gossip: {
    keywords: ['明星绯闻', '职场秘闻', '校园八卦'],
    npcs: [
      { name: '吃瓜第一线', style: '普通用户' },
      { name: '八卦爆料机', style: '版主' },
      { name: '路过的蚂蚁', style: '普通用户' }
    ],
    templates: [
      "【{keyword}】今天在公司茶水间，竟然听到老板和新来的实习生在说...当时我整个人都惊呆了！原来上周那个大项目突然换人是因为这个！实习生还拿出了一个U盘，说里面有所有的账目流水。我吓得连咖啡都没拿就溜了，现在手还在抖，这事要是被发现了我会不会被灭口啊？",
      "【{keyword}】惊天大瓜！某顶流被拍深夜进出神秘公寓，知情人爆料说他早就隐婚生子了！而且女方还是圈内某个一直立单身人设的小花！据说狗仔手里还有更锤的视频，周二见！我朋友在公关公司，说他们现在已经乱成一锅粥了，连夜开会商量对策，这波估计是要塌房塌得彻彻底底了！",
      "【{keyword}】我们学校那个出了名的高冷校草，昨天被人看到在操场角落里被一个女生壁咚！而且那个女生还是隔壁职高的！校草平时对谁都爱搭不理的，结果当时居然脸红了，还乖乖任由对方捏脸！这反差感绝了，有没有人知道那个女生到底是谁啊，太牛了吧！"
    ]
  },
  entertainment: {
    keywords: ['新片上映', '综艺名场面', '明星穿搭'],
    npcs: [
      { name: '爱吐槽的阿花', style: '娱乐版主' },
      { name: '资深影评人', style: '普通用户' },
      { name: '颜狗本狗', style: '普通用户' }
    ],
    templates: [
      "【{keyword}】刚看完那部吹上天的新电影，就这？剧情稀碎，逻辑根本不通，男主的演技像块木头，全程一个表情。特效五毛钱不能再多了，最后那个强行煽情简直把我尬得脚趾抠出三室一厅！避雷避雷，千万别去电影院浪费钱，等网播都嫌浪费时间！",
      "【{keyword}】昨晚那期综艺简直封神了好吗！某某某在游戏环节那个下意识的保护动作太苏了，而且他后来输了被惩罚的时候，那个委屈巴巴的小眼神，我的心都要化了！这段我反复观看了十遍，CP粉已经过年了，民政局我给你们搬过来，请原地结婚！",
      "【{keyword}】某红毯造型大赏，这次真的是神仙打架！不过最惊艳我的还是某女星的那套高定，那个剪裁，那个质感，走起路来波光粼粼的，简直就是人鱼公主本主！相比之下，某位一直营销美貌的就翻车了，那身衣服像裹着床单就出来了，造型师扣鸡腿！"
    ]
  },
  horror: {
    keywords: ['深夜怪谈', '古宅探险', '灵异事件'],
    npcs: [
      { name: '灵异爱好者小宇', style: '恐怖板块NPC' },
      { name: '胆小鬼', style: '普通用户' },
      { name: '道长在此', style: '版主' }
    ],
    templates: [
      "【{keyword}】昨晚加班到凌晨，路过公司后巷的老槐树时，突然听见有人在叫我的名字。声音很细，像是个小女孩。我没回头，加快脚步想走，结果发现地上的影子变成了两个！我拼命往前跑，直到跑到有路灯的大街上才敢停下。今天打听了一下，原来那棵树下以前...",
      "【{keyword}】和朋友去废弃的医院探险。走到地下太平间的时候，我朋友的手机突然响了。可是那里根本没有信号！接通后，里面只有沉重的呼吸声，和指甲刮擦玻璃的声音。我们吓得夺门而出，结果在跑出大门的时候，我回头看了一眼二楼的窗户，有个穿着病号服的人正死死地盯着我们...",
      "【{keyword}】刚搬进二手房，每天半夜都能听到楼上弹钢琴的声音。去敲门也没人理。昨天忍不住找了物业，物业大爷脸色苍白地告诉我，楼上那户人家十年前就出了意外，根本没人住！那我每天晚上听到的琴声到底是哪里来的？而且，我现在发现，那琴声好像是从我床底下传出来的..."
    ]
  }
};

const commentTemplates = [
  "卧槽这也太扯了吧😱",
  "蹲后续！求爆料！",
  "前排吃瓜🍉",
  "细思极恐...",
  "真的假的？太劲爆了吧！",
  "楼主注意安全啊！",
  "这瓜保熟吗？",
  "不敢看了，先马后看",
  "太离谱了，小说都不敢这么写",
  "打卡，坐等更新"
];

function switchForumTab(tab) {
  currentForumTab = tab;
  document.querySelectorAll('.forum-tab').forEach(el => {
    el.classList.remove('active');
    el.style.color = 'var(--text-light)';
    el.style.borderBottom = '2px solid transparent';
    el.style.fontWeight = 'normal';
  });
  const activeTab = document.querySelector(\`.forum-tab[onclick="switchForumTab('\${tab}')"]\`);
  if(activeTab) {
    activeTab.classList.add('active');
    activeTab.style.color = 'var(--main-pink)';
    activeTab.style.borderBottom = '2px solid var(--main-pink)';
    activeTab.style.fontWeight = 'bold';
  }
  refreshForum();
}

function generateRandomId() {
  return Date.now().toString().slice(-6) + Math.random().toString(36).slice(2, 6);
}

function generateRelativeTime() {
  const times = ['刚刚', '1分钟前', '5分钟前', '10分钟前', '半小时前', '1小时前', '2小时前'];
  return times[Math.floor(Math.random() * times.length)];
}

function refreshForum() {
  const container = document.getElementById('forum-content');
  if(!container) return;
  container.innerHTML = '<div style="text-align:center; padding:20px; color:#999;">正在加载新帖子...</div>';
  
  setTimeout(() => {
    container.innerHTML = '';
    const data = forumData[currentForumTab];
    
    for (let i = 0; i < 5; i++) {
      const keyword = data.keywords[Math.floor(Math.random() * data.keywords.length)];
      const template = data.templates[Math.floor(Math.random() * data.templates.length)];
      const content = template.replace('{keyword}', keyword);
      const title = content.substring(0, 15) + '...';
      const userId = '用户_' + generateRandomId();
      const time = generateRelativeTime();
      
      const postEl = document.createElement('div');
      postEl.style.cssText = 'background: #fff; border-radius: 12px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);';
      
      // Comments
      let commentsHtml = '';
      const numComments = Math.floor(Math.random() * 3) + 3; // 3-5 comments
      for (let j = 0; j < numComments; j++) {
        const isNpc = Math.random() > 0.5;
        let commenterName, commenterStyle;
        if (isNpc) {
          const npc = data.npcs[Math.floor(Math.random() * data.npcs.length)];
          commenterName = npc.name;
          commenterStyle = \`<span style="background:var(--light-pink); color:var(--main-pink); font-size:10px; padding:2px 4px; border-radius:4px; margin-left:4px;">\${npc.style}</span>\`;
        } else {
          commenterName = '用户_' + generateRandomId();
          commenterStyle = '';
        }
        
        const commentContent = commentTemplates[Math.floor(Math.random() * commentTemplates.length)];
        const likes = Math.floor(Math.random() * 100) + 1;
        
        commentsHtml += \`
          <div style="margin-bottom: 8px; font-size: 13px; border-bottom: 1px dashed #eee; padding-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
              <span style="color: #666; font-weight: bold;">\${commenterName} \${commenterStyle}</span>
              <span style="color: #999; font-size: 12px;">👍 \${likes}</span>
            </div>
            <div style="color: #333;">\${commentContent}</div>
            <div style="color: var(--main-pink); font-size: 12px; margin-top: 4px; cursor: pointer;" onclick="alert('回复功能开发中')">回复</div>
          </div>
        \`;
      }
      
      postEl.innerHTML = \`
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 36px; height: 36px; border-radius: 50%; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 18px;">👤</div>
            <div>
              <div style="font-weight: bold; font-size: 14px; color: #333;">\${userId}</div>
              <div style="font-size: 12px; color: #999;">\${time}</div>
            </div>
          </div>
        </div>
        <div style="font-weight: bold; font-size: 16px; margin-bottom: 8px; color: #222;">\${title}</div>
        <div style="font-size: 14px; color: #444; line-height: 1.6; max-height: 200px; overflow-y: auto; margin-bottom: 15px; padding-right: 5px;">
          \${content}
        </div>
        <div style="background: #f9f9f9; border-radius: 8px; padding: 10px;">
          <div style="font-size: 12px; color: #999; margin-bottom: 8px;">热门评论</div>
          \${commentsHtml}
        </div>
      \`;
      container.appendChild(postEl);
    }
  }, 500);
}

// Hook into openSub to refresh forum when opened
document.addEventListener('DOMContentLoaded', () => {
    const originalOpenSub = window.openSub;
    if(originalOpenSub) {
        window.openSub = function(id) {
            originalOpenSub(id);
            if (id === 'forum-page') {
                refreshForum();
            }
        };
    }
});
`;
    
    if (!html.includes('let currentForumTab')) {
        html = html.replace('</script>\n</body>', forumJs + '\n</script>\n</body>');
    }

    fs.writeFileSync('index.html', html, 'utf-8');
}

updateIndexHtml();
