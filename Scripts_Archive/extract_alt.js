Line 1851 :   if (!msg.alternatives || msg.alternatives.length <= 1) return;
Line 1852 :   const maxIndex = msg.alternatives.length - 1;
Line 1853 :   if (direction === 'prev') {
Line 1854 :     msg.currentIndex = (msg.currentIndex > 0) ? msg.currentIndex - 1 : maxIndex;
Line 1855 :   } else {
Line 1856 :     msg.currentIndex = (msg.currentIndex < maxIndex) ? msg.currentIndex + 1 : 0;
Line 1857 :   }
Line 1858 :   const chosen = msg.alternatives[msg.currentIndex];
Line 1859 :   msg.content = chosen.content;
Line 1860 :   if (chosen.statusData) msg.statusData = chosen.statusData;
Line 1861 :   saveToStorage('CHAT_RECORDS', JSON.stringify(chatRecords)).then(() => {
Line 1862 :     renderChat();
Line 1863 :   });
Line 1864 : }
Line 1865 : 
Line 1866 : function addMsgToUI(content, side, avatar, quote, idx, type, skipScroll = false, senderName = null, statusData = null, isOfflineMsg = undefined) {
Line 1867 :   // 注意：表情包处理已移到 createMsgElement -> parseTextBeautify 之后执行
Line 1868 :   // 避免 <img> 标签被 parseTextBeautify 的 HTML 转义所破坏
Line 1869 :   const el = document.getElementById('chatContent');
Line 1870 :   const div = createMsgElement(content, side, avatar, quote, idx, type, senderName, statusData, isOfflineMsg);
Line 1871 :   el.appendChild(div);
Line 1872 :   
Line 1873 :   if (!skipScroll) {
Line 1874 :     el.scrollTop = el.scrollHeight;
Line 1875 :   }
Line 1876 : 
Line 1877 :   if (chatSettings.hideAvatar) {
Line 1878 :     const newAvatar = div.querySelector('.msg-avatar');
Line 1879 :     if (newAvatar) newAvatar.style.display = 'none';
Line 1880 :   }
Line 1881 : }
Line 1882 : 
Line 1883 : // 全屏查看图片
Line 1884 : function viewFullImage(src) {
Line 1885 :   const viewer = document.createElement('div');
Line 1886 :   viewer.style.cssText = 'position:fixed; inset:0; background:rgba(0,0,0,0.92); z-index:99999; display:flex; align-items:center; justify-content:center; cursor:zoom-out;';
Line 1887 :   const img = document.createElement('img');
Line 1888 :   img.src = src;
Line 1889 :   img.style.cssText = 'max-width:92%; max-height:92%; object-fit:contain; border-radius:10px; box-shadow:0 8px 40px rgba(0,0,0,0.5);';
Line 1890 :   viewer.appendChild(img);
Line 1891 :   viewer.onclick = () => viewer.remove();
Line 1892 :   document.body.appendChild(viewer);
Line 1893 : }
Line 1894 : 
Line 1895 : function updateSelectedCount() {
Line 1896 :   document.getElementById('selectedCount').innerText = `已选 ${selectedMsgIndices.length} 条`;
Line 1897 : }
Line 1898 : 
Line 1899 : function replyToMsg(content, btn) {
Line 1900 :   let short = content.length > 15 ? content.slice(0,15)+'...' : content;
