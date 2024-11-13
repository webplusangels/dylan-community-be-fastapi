const express = require('express');
const path = require('path');

const router = express.Router();

// 프론트엔드 페이지가 위치하는 디렉토리 설정
const pagesDir = path.join(__dirname, '../../frontend/pages');

// 각 페이지 라우트 설정
router.get('/', (req, res) => {
    res.sendFile(path.join(pagesDir, 'index.html')); // 기본 페이지
});

router.get('/login', (req, res) => {
    res.sendFile(path.join(pagesDir, 'login.html'));
});

router.get('/signup', (req, res) => {
    res.sendFile(path.join(pagesDir, 'signup.html'));
});

router.get('/profile', (req, res) => {
    res.sendFile(path.join(pagesDir, 'profile.html'));
});

router.get('/edit_profile', (req, res) => {
    res.sendFile(path.join(pagesDir, 'edit_profile.html'));
});

router.get('/edit_password', (req, res) => {
    res.sendFile(path.join(pagesDir, 'edit_password.html'));
});

router.get('/make_post', (req, res) => {
    res.sendFile(path.join(pagesDir, 'make_post.html'));
});

router.get('/posts', (req, res) => {
    res.sendFile(path.join(pagesDir, 'posts.html'));
});

router.get('/post/:id', (req, res) => {
    // const postId = req.params.id; // 게시물 ID를 가져오기
    res.sendFile(path.join(pagesDir, 'post.html')); // 해당 게시물 페이지로 이동
});

// 404 페이지 라우트 (찾을 수 없는 페이지)
router.use((req, res) => {
    res.status(404).send('Page not found');
});

module.exports = router;
