const express = require('express');
const userController = require('../controllers/userController');

const router = express.Router();

// 사용자 목록 조회 라우트
router.get('/', userController.getUsers);

// 패스워드 재설정 라우트
router.put('/reset-password', userController.resetPassword);

// 현재 사용자 프로필 조회 라우트
router.get('/me', userController.getProfile);

// 현재 사용자 프로필 수정 라우트
router.put('/me', userController.updateProfile);

// 현재 사용자 프로필 삭제 라우트
router.delete('/me', userController.deleteProfile);

module.exports = router;
