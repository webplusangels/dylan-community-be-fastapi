const commentModel = require('../models/commentModel');
const { ERROR_MESSAGES } = require('../constants');

// 댓글 id로 단일 댓글 조회
const getCommentById = async (req, res) => {
    const { commentId } = req.params;

    try {
        const comment = await commentModel.getCommentById(commentId);
        if (!comment) {
            res.status(404).json({
                message: '댓글을 찾을 수 없습니다.',
            });
            return;
        }
        res.status(200).json(comment);
    } catch (err) {
        console.error('댓글 조회 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 페이지네이션된 댓글 목록 조회
const getPaginatedComments = async (req, res) => {
    const { postId } = req.params;
    const { page = 1, limit = 10 } = req.query;

    try {
        const comments = await commentModel.getPaginatedComments(
            postId,
            Number(page),
            Number(limit)
        );
        res.status(200).json(comments);
    } catch (err) {
        console.error('댓글 조회 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

module.exports = {
    getCommentById,
    getPaginatedComments,
};
