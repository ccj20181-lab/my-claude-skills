const fs = require('fs');
const path = require('path');

const srcDir = 'C:\\Users\\cj\\Desktop';
const destDir = 'F:\\研究报告下载\\液冷产业';

if (!fs.existsSync(destDir)){
    fs.mkdirSync(destDir, { recursive: true });
}

fs.readdir(srcDir, (err, files) => {
    if (err) {
        console.error('无法读取源目录:', err);
        return;
    }

    let count = 0;
    files.forEach(file => {
        if (file.startsWith('[研报]_') && file.endsWith('.pdf')) {
            const srcPath = path.join(srcDir, file);
            const destPath = path.join(destDir, file);

            try {
                fs.renameSync(srcPath, destPath);
                console.log(`✅ 移动: ${file}`);
                count++;
            } catch (moveErr) {
                console.error(`❌ 移动失败 ${file}: ${moveErr.message}`);
            }
        }
    });
    console.log(`\n🎉 完成！共移动 ${count} 份报告。`);
});
