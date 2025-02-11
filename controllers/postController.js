/* eslint-disable camelcase */
const postModel = require('../models/postModel');
const { getUploadedFileUrl } = require('../utils/uploadUtils');

// id로 단일 포스트 조회
const getPostById = async (req, res, next) => {
    const { id } = req.params;

    try {
        // 좋아요 수 업데이트
        await postModel.updatePostLikesById(id);
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
        next(err);
    }
};

// 페이지네이션된 포스트 목록 조회
const getPaginatedPosts = async (req, res, next) => {
    let { lastCreatedAt, limit } = req.query;

    // 쿼리스트링 유효성 검사
    limit = parseInt(limit, 10) || 100; // 기본값: 100
    limit = Math.min(Math.max(limit, 1), 100); // 1부터 최대 100까지
    lastCreatedAt = lastCreatedAt ? new Date(lastCreatedAt) : new Date(); // 기본값: 현재 시간

    try {
        // 데이터베이스에서 데이터 가져오기
        const posts = await postModel.getPaginatedPosts(lastCreatedAt, limit);

        // 결과 반환
        res.status(200).json(posts);
    } catch (err) {
        console.error('포스트 목록 조회 오류:', err);
        next(err);
    }
};

// 포스트 생성
const createPost = async (req, res, next) => {
    const { user } = req;
    const { title, content, image_path } = req.body;

    // 필수 필드 검증
    if (!title || !content) {
        res.status(400).json({
            message: '제목과 내용은 필수 입력 항목입니다.',
        });
        return;
    }

    // 사용자 검증
    if (!user.user_id) {
        res.status(401).json({
            message: '권한이 없습니다.',
        });
        return;
    }

    try {
        const postId = await postModel.createPost(
            { title, content, image_path },
            user.user_id
        );
        const post_id = await postModel.getPostIdById(postId);
        res.status(201).json({ message: '포스트 작성 완료', post_id });
    } catch (err) {
        console.error('포스트 생성 오류:', err);
        next(err);
    }
};

// 포스트 수정
const updatePostById = async (req, res, next) => {
    const { id } = req.params;
    const { title, content, image_path } = req.body;

    // 필수 필드 검증
    if (!title || !content) {
        res.status(400).json({
            message: '제목과 내용은 필수 입력 항목입니다.',
        });
        return;
    }

    // JWT 검증
    const { user } = req;
    if (!user || !user.user_id) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
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
        if (post.user_id !== user.user_id) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }

        const post_id = await postModel.updatePostById(
            { title, content, image_path },
            id
        );
        res.status(200).json({ message: '포스트 수정 완료', post_id });
    } catch (err) {
        console.error('포스트 수정 오류:', err);
        next(err);
    }
};

// 포스트 삭제
const deletePostById = async (req, res, next) => {
    const { id } = req.params;
    const { user } = req;

    // 로그인 상태 확인
    if (!user || !user.user_id) {
        res.status(401).json({
            message: '로그인이 필요합니다.',
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
        if (post.user_id !== user.user_id) {
            res.status(403).json({
                message: '권한이 없습니다.',
            });
            return;
        }

        await postModel.deletePostById(id);
        res.status(200).json({ message: '포스트 삭제 완료' });
    } catch (err) {
        console.error('포스트 삭제 오류:', err);
        next(err);
    }
};

// 포스트 메타 정보 조회
const getPostMetaById = async (req, res, next) => {
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
        next(err);
    }
};

// 포스트 이미지 업로드
const uploadPostImages = (req, res, next) => {
    try {
        const fileUrl = getUploadedFileUrl(req.file);
        res.status(200).json({ url: fileUrl });
    } catch (err) {
        console.error('Post 이미지 업로드 오류:', err);
        next(err);
    }
};

// 좋아요 토글
const toggleLike = async (req, res, next) => {
    try {
        const { user } = req;
        if (!user || !user.user_id) {
            res.status(401).json({
                message: '로그인이 필요합니다.',
            });
            return;
        }

        const { postId } = req.params;

        const { isLike, updatedLikes } = await postModel.toggleLike(
            postId,
            user.user_id
        );
        res.status(200).json({ isLike, likes: updatedLikes });
    } catch (err) {
        console.error('포스트 좋아요 토글 오류:', err);
        next(err);
    }
};

// 좋아요 상태 조회
const getLikeStatus = async (req, res, next) => {
    try {
        const { user } = req;
        if (!user || !user.user_id) {
            res.status(401).json({
                message: '로그인이 필요합니다.',
            });
            return;
        }

        const { postId } = req.params;
        const isLike = await postModel.getLikeStatus(postId, user.user_id);

        res.status(200).json({ isLike });
    } catch (err) {
        console.error('포스트 좋아요 상태 조회 오류:', err);
        next(err);
    }
};

// 댓글 수 업데이트
const getCommentCount = async (req, res, next) => {
    const { postId } = req.params;

    try {
        const count = await postModel.updatePostCommentsCountById(postId);
        res.status(200).json({ count });
    } catch (err) {
        console.error('포스트 댓글 수 조회 오류:', err);
        next(err);
    }
};

// 조회수 업데이트
const incrementPostView = async (req, res, next) => {
    const { postId } = req.params;

    try {
        await postModel.updatePostViewById(postId);
        res.status(200).json({ message: '조회수 증가 완료' });
    } catch (err) {
        console.error('조회수 증가 오류:', err);
        next(err);
    }
};

module.exports = {
    getPostById,
    getPaginatedPosts,
    createPost,
    updatePostById,
    deletePostById,
    getPostMetaById,
    uploadPostImages,
    toggleLike,
    getLikeStatus,
    getCommentCount,
    incrementPostView,
};
