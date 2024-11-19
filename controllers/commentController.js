const commentModel = require('../models/commentModel');

// 댓글 id로 단일 댓글 조회
const getCommentById = async (req, res, next) => {
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
        next(err);
    }
};

// 댓글 생성
const createComment = async (req, res, next) => {
    const { postId } = req.params;
    const { content } = req.body;

    // 필수 필드 검증
    if (!content) {
        res.status(400).json({
            message: '내용은 필수 입력 항목입니다.',
        });
        return;
    }

    // 세션 검증
    if (!req.session.user) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
        });
        return;
    }
    const userId = req.session.user.user_id;

    try {
        const commentId = await commentModel.createComment(
            { content },
            postId,
            userId
        );
        // 댓글 수 업데이트
        await commentModel.updateCommentsCountById(postId);
        res.status(201).json({
            comment_id: commentId,
        });
    } catch (err) {
        console.error('댓글 생성 오류:', err);
        next(err);
    }
};

// 댓글 수정
const updateComment = async (req, res, next) => {
    const { commentId } = req.params;
    const { content } = req.body;

    // 필수 필드 검증
    if (!content) {
        res.status(400).json({
            message: '내용은 필수 입력 항목입니다.',
        });
        return;
    }

    // 세션 검증
    if (!req.session.user) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
        });
        return;
    }
    const userId = req.session.user.user_id;

    try {
        const updatedComment = await commentModel.updateCommentById(
            content,
            commentId
        );
        if (!updatedComment) {
            res.status(404).json({
                message: '댓글을 찾을 수 없습니다.',
            });
            return;
        }

        // 댓글 작성자 검증
        if (updatedComment.user_id !== userId) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }
        res.status(200).json(updatedComment);
    } catch (err) {
        console.error('댓글 수정 오류:', err);
        next(err);
    }
};

// 페이지네이션된 댓글 목록 조회
const getPaginatedComments = async (req, res, next) => {
    const { postId } = req.params;
    let { lastCreatedAt, limit } = req.query;

    // 쿼리스트링 유효성 검사
    limit = Math.min(Math.max(parseInt(limit, 10) || 10, 1), 100); // 1부터 최대 100까지
    lastCreatedAt = lastCreatedAt ? new Date(lastCreatedAt) : new Date(); // 기본값: 현재 시간

    try {
        // 데이터베이스에서 데이터 가져오기
        const comments = await commentModel.getPaginatedComments(
            postId,
            lastCreatedAt,
            limit
        );

        // 결과 반환
        res.status(200).json(comments);
    } catch (err) {
        console.error('댓글 목록 조회 오류:', err);
        next(err);
    }
};

// 댓글 삭제
const deleteComment = async (req, res, next) => {
    const { commentId } = req.params;

    // 세션 검증
    if (!req.session.user) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
        });
        return;
    }
    const userId = req.session.user.user_id;

    try {
        const comment = await commentModel.getCommentById(commentId);
        if (!comment) {
            res.status(404).json({
                message: '댓글을 찾을 수 없습니다.',
            });
            return;
        }

        // 댓글 작성자 검증
        if (comment.user_id !== userId) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }

        // 댓글 업데이트
        await commentModel.updateCommentsCountById(comment.post_id);
        await commentModel.deleteCommentById(commentId);
        res.status(200).json({ message: '댓글 삭제 완료' });
    } catch (err) {
        console.error('댓글 삭제 오류:', err);
        next(err);
    }
};

module.exports = {
    getCommentById,
    createComment,
    updateComment,
    getPaginatedComments,
    deleteComment,
};
