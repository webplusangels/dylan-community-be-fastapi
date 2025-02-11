const commentModel = require('../models/commentModel');
const { getById } = require('../utils/utils');

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
    const { user } = req;
    if (!user || !user.user_id) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
        });
        return;
    }

    try {
        await commentModel.createComment({ content }, postId, user.user_id);
        // 댓글 수 업데이트
        await commentModel.updateCommentsCountById(postId);
        const comments = await commentModel.getCommentsByPostId(postId);
        res.status(201).json({
            message: '댓글 생성 완료',
            comments,
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
    const { user } = req;
    if (!user || !user.user_id) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
        });
        return;
    }

    try {
        const existingComment = await getById(
            'comments',
            commentId,
            'comment_id'
        );
        if (!existingComment) {
            res.status(404).json({
                message: '댓글을 찾을 수 없습니다.',
            });
            return;
        }

        // 댓글 작성자 검증
        if (existingComment.user_id !== user.user_id) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }
        const updatedComment = await commentModel.updateCommentById(
            content,
            commentId
        );
        const comments = await commentModel.getCommentsByPostId(
            updatedComment.post_id
        );
        res.status(201).json({
            message: '댓글 생성 완료',
            comments,
        });
        res.status(200).json(updatedComment);
    } catch (err) {
        console.error('댓글 수정 오류:', err);
        next(err);
    }
};

// 페이지네이션된 댓글 목록 조회
const getPaginatedComments = async (req, res, next) => {
    const { postId } = req.params;
    let { firstCreatedAt, limit } = req.query;

    // 쿼리스트링 유효성 검사
    limit = Math.min(Math.max(parseInt(limit, 10) || 100, 1), 100); // 1부터 최대 100까지
    firstCreatedAt = firstCreatedAt ? new Date(firstCreatedAt) : new Date(); // 기본값: 현재 시간

    try {
        // 데이터베이스에서 데이터 가져오기
        const comments = await commentModel.getPaginatedComments(
            postId,
            limit,
            firstCreatedAt
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
    const { user } = req;
    if (!user || !user.user_id) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
        });
        return;
    }

    try {
        const comment = await commentModel.getCommentById(commentId);
        if (!comment) {
            res.status(404).json({
                message: '댓글을 찾을 수 없습니다.',
            });
            return;
        }

        // 댓글 작성자 검증
        if (comment.user_id !== user.user_id) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }
        // 댓글 업데이트
        await commentModel.updateCommentsCountById(comment.post_id);
        await commentModel.deleteCommentById(commentId);
        const comments = await commentModel.getCommentsByPostId(
            comment.post_id
        );
        res.status(200).json({ message: '댓글 삭제 완료', comments });
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
