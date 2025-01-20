const express = require('express');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
const upload = require('../config/multerConfig');
const userController = require('../controllers/userController');
const postController = require('../controllers/postController');

const router = express.Router();

// 업로드 함수
const handleUpload = (req, res, next) => {
    upload.single('image')(req, res, (err) => {
        if (err) {
            if (err instanceof multer.MulterError) {
                if (err.code === 'LIMIT_FILE_SIZE') {
                    console.error('파일 크기 초과:', err);
                    res.status(400).json({
                        message: '파일 크기가 너무 큽니다. (최대 5MB)',
                    });
                    return;
                }
                console.error('Multer 오류:', err);
                res.status(400).json({
                    message: '이미지 업로드에 실패했습니다.',
                });
                return;
            }
            console.error('이미지 업로드 오류:', err);
            res.status(500).json({
                message: '서버 오류가 발생했습니다.',
            });
        }
        next();
    });
};

// Post 이미지 업로드
router.post('/post-images', handleUpload, postController.uploadPostImages);

// User 프로필 이미지 업로드
router.post('/profile-image', handleUpload, userController.uploadProfileImage);

// 이미지 조회
router.get(`/:imagePath`, (req, res) => {
    const { imagePath } = req.params;
    const imgPath = path.join(__dirname, '../uploads', imagePath);

    if (fs.existsSync(imgPath)) {
        res.sendFile(imgPath);
        return;
    }
    res.status(404).json({ message: '이미지를 찾을 수 없습니다.' });
});

module.exports = router;
