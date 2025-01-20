const express = require('express');
const userController = require('../controllers/userController');

const router = express.Router();

// 세션 확인 라우트
router.get('/session', userController.getSession);

// 회원가입 라우트
router.post('/signup', userController.addUser);

// 로그인 라우트
router.post('/login', userController.loginUser);

// 로그아웃 라우트
router.delete('/logout', userController.logoutUser);

// 이메일 중복 확인 라우트
router.post('/check-email', userController.checkEmail);

module.exports = router;
