const fs = require('fs');
const content = fs.readFileSync('js/main.js', 'utf8');

// Find all functions containing contact
const matches = content.match(/function\s+\w*contact\w*\s*\(/gi);
console.log("Functions containing 'contact':", matches);

// Let's also find where contactMemo is updated in the UI
const memoMatches = content.match(/.{0,50}contactMemo.{0,50}/g);
console.log("\ncontactMemo usage:");
memoMatches.forEach(m => console.log(m.trim()));
