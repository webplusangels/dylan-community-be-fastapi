const express = require('express');
const userController = require('../controllers/userController');

const router = express.Router();

// 패스워드 재설정 라우트
router.put('/password', userController.resetPassword);

// 현재 사용자 프로필 조회 라우트
router.get('/me', userController.getProfile);

// 현재 사용자 프로필 수정 라우트
router.put('/me', userController.updateProfile);

// 현재 사용자 프로필 삭제 라우트
router.delete('/me', userController.deleteProfile);

module.exports = router;
