const fs = require('fs');

try {
    const html = fs.readFileSync('index.html', 'utf8');
    const scripts = html.match(/<script>([\s\S]*?)<\/script>/g);
    
    if (scripts && scripts.length > 0) {
        const lastScript = scripts[scripts.length - 1].replace(/<\/?script>/g, '');
        fs.writeFileSync('temp.js', lastScript);
        console.log('Script extracted to temp.js');
    } else {
        console.log('No scripts found');
    }
} catch (e) {
    console.error('Error:', e);
}