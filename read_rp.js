const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf-8');

const openRedPacketMatch = content.match(/function openRedPacket\([\s\S]*?\n  \}/);
if (openRedPacketMatch) {
  console.log("=== openRedPacket ===");
  console.log(openRedPacketMatch[0]);
}

const createMsgMatch = content.match(/function createMsgElement\([\s\S]*?\n  \}/);
if (createMsgMatch) {
  console.log("=== createMsgElement ===");
  // Print only parts of createMsgElement to avoid flooding
  const lines = createMsgMatch[0].split('\n');
  lines.forEach((l, i) => {
    if (l.includes('openRedPacket') || l.includes('rp')) {
      console.log(i, l);
    }
  });
}
