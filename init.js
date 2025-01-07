const fs = require('fs');
const path = require('path');

// 생성할 폴더 목록
const folders = [path.join(__dirname, 'uploads')];

// 폴더 생성 함수
folders.forEach((folder) => {
    if (!fs.existsSync(folder)) {
        fs.mkdirSync(folder, { recursive: true });
        console.log(`폴더 생성 완료: ${folder}`);
    } else {
        console.log(`폴더가 이미 존재합니다: ${folder}`);
    }
});
