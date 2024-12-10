// multer 설정
const fs = require('fs');
const multer = require('multer');
const dotenv = require('dotenv');

dotenv.config();

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = 'uploads/';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const sanitizedFilename = file.originalname
            .replace(/[^a-zA-Z0-9.\-_]/g, '') // 알파벳, 숫자, ., -, _만 허용
            .toLowerCase(); // 소문자로 변환
        cb(null, `${Date.now()}-${sanitizedFilename}`);
    },
});

const fileFilter = (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (allowedTypes.includes(file.mimetype)) {
        cb(null, true); // 허용
    } else {
        cb(new Error('이미지 파일만 업로드할 수 있습니다.'), false); // 차단
    }
};

const upload = multer({
    storage,
    limits: { fileSize: process.env.MAX_FILE_SIZE || 5 * 1024 * 1024 }, // 기본값: 5MB
    fileFilter,
});

module.exports = upload;
