const express = require('express');
const commentController = require('../controllers/commentController');

const router = express.Router();

// 댓글 id로 댓글 조회 라우트
router.get('/:commentId', commentController.getCommentById);

module.exports = router;
