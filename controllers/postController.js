const postModel = require('../models/postModel');
const { ERROR_MESSAGES } = require('../constants');

// id로 단일 포스트 조회
const getPostById = async (req, res) => {
    const { id } = req.params;

    try {
        const post = await postModel.getPostById(id);
        if (!post) {
            res.status(404).json({
                message: '포스트를 찾을 수 없습니다.',
            });
            return;
        }
        res.status(200).json(post);
    } catch (err) {
        console.error('포스트 조회 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 페이지네이션된 포스트 목록 조회
const getPaginatedPosts = async (req, res) => {
    let { page, limit } = req.query;

    page = Number(page);
    limit = Number(limit);

    // 유효성 검사
    if (Number.isNaN(page) || Number.isNaN(limit) || page <= 0 || limit <= 0) {
        res.status(400).json({
            message: '유효하지 않은 쿼리 파라미터입니다.',
        });
        return;
    }

    try {
        const posts = await postModel.getPaginatedPosts(page, limit);
        res.status(200).json(posts);
    } catch (err) {
        console.error('포스트 목록 조회 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 포스트 생성
const createPost = async (req, res) => {
    const { title, content } = req.body;
    const userId = req.session.user.user_id;

    // 필수 필드 검증
    if (!title || !content) {
        res.status(400).json({
            message: '제목과 내용은 필수 입력 항목입니다.',
        });
        return;
    }

    // 사용자 검증
    if (!userId) {
        res.status(401).json({
            message: '권한이 없습니다.',
        });
        return;
    }

    try {
        const postId = await postModel.createPost({ title, content }, userId);
        res.status(201).json({ message: '포스트 작성 완료', post_id: postId });
    } catch (err) {
        console.error('포스트 생성 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 포스트 수정
const updatePostById = async (req, res) => {
    const { id } = req.params;
    const { title, content } = req.body;
    const userId = req.session.user.user_id;

    // 필수 필드 검증
    if (!title || !content) {
        res.status(400).json({
            message: '제목과 내용은 필수 입력 항목입니다.',
        });
        return;
    }

    try {
        const post = await postModel.getPostById(id);
        if (!post) {
            res.status(404).json({
                message: '포스트를 찾을 수 없습니다.',
            });
            return;
        }

        // 사용자 검증
        if (post.user_id !== userId) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }

        await postModel.updatePostById(id, { title, content });
        res.status(200).json({ message: '포스트 수정 완료' });
    } catch (err) {
        console.error('포스트 수정 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 포스트 삭제
const deletePostById = async (req, res) => {
    const { id } = req.params;

    // 로그인 상태 확인
    if (!req.session.user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    const userId = req.session.user.user_id;

    try {
        const post = await postModel.getPostById(id);
        if (!post) {
            res.status(404).json({
                message: '포스트를 찾을 수 없습니다.',
            });
            return;
        }

        // 사용자 검증
        if (post.user_id !== userId) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }

        await postModel.deletePostById(id);
        res.status(200).json({ message: '포스트 삭제 완료' });
    } catch (err) {
        console.error('포스트 삭제 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 포스트 메타 정보 조회
const getPostMetaById = async (req, res) => {
    const { id } = req.params;

    try {
        const post = await postModel.getPostMetaById(id);
        if (!post) {
            res.status(404).json({
                message: '포스트를 찾을 수 없습니다.',
            });
            return;
        }
        res.status(200).json(post);
    } catch (err) {
        console.error('포스트 메타 정보 조회 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

// 포스트 메타 정보 업데이트
const updatePostMetaById = async (req, res) => {
    const { id } = req.params;
    const { views, likes, comments_count } = req.body;

    try {
        const post = await postModel.getPostMetaById(id);
        if (!post) {
            res.status(404).json({
                message: '포스트를 찾을 수 없습니다.',
            });
            return;
        }

        await postModel.updatePostMetaById(id, {
            views,
            likes,
            comments_count,
        });
        res.status(200).json({ message: '포스트 메타 정보 업데이트 완료' });
    } catch (err) {
        console.error('포스트 메타 정보 업데이트 오류:', err);
        res.status(500).json({
            message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        });
    }
};

module.exports = {
    getPostById,
    getPaginatedPosts,
    createPost,
    updatePostById,
    deletePostById,
    getPostMetaById,
    updatePostMetaById,
};
