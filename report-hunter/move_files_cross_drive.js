const fs = require('fs');
const path = require('path');

const srcDir = 'C:\\Users\\cj\\Desktop';
const destDir = 'F:\\研究报告下载\\液冷产业';

// 确保目标目录存在
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
                // 跨盘移动策略：先复制，后删除
                fs.copyFileSync(srcPath, destPath);
                fs.unlinkSync(srcPath);
                console.log(`✅ 移动成功: ${file}`);
                count++;
            } catch (moveErr) {
                console.error(`❌ 移动失败 ${file}: ${moveErr.message}`);
            }
        }
    });
    console.log(`\n🎉 完成！共移动 ${count} 份报告至 ${destDir}`);
});
