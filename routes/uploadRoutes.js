const express = require('express');
const path = require('path');
const fs = require('fs');
const upload = require('../config/multerConfig');
const userController = require('../controllers/userController');
const postController = require('../controllers/postController');

const router = express.Router();

// Post 이미지 업로드
router.post(
    '/post-images',
    upload.single('image'),
    postController.uploadPostImages
);

// User 프로필 이미지 업로드
router.post(
    '/profile-image',
    upload.single('image'),
    userController.uploadProfileImage
);

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
