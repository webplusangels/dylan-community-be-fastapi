const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const commentsDataPath = path.join(__dirname, '../data/comments.json');

// 댓글 데이터를 읽어오는 함수
const getComments = async () => {
    try {
        const data = await fs.readFile(commentsDataPath, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        console.error('JSON 파일 읽기 오류:', error);
        throw error;
    }
};

// 댓글 ID로 단일 댓글 조회 함수
const getCommentById = async (id) => {
    try {
        const comments = await getComments();
        const commentData = comments.find(
            (comment) => comment.comment_id === Number(id)
        );
        if (!commentData) {
            return null;
        }
        return commentData;
    } catch (error) {
        console.error('댓글 데이터 조회 오류:', error);
        throw error;
    }
};

// 댓글 데이터를 저장하는 함수
const saveComments = async (comments) => {
    try {
        await fs.writeFile(
            commentsDataPath,
            JSON.stringify(comments, null, 2),
            'utf-8'
        );
    } catch (error) {
        console.error('JSON 파일 쓰기 오류:', error);
        throw error;
    }
};

// 댓글 생성 함수
const createComment = async (comment, postId, userId) => {
    try {
        const comments = await getComments();
        const newComment = {
            comment_id: uuidv4(),
            post_id: Number(postId),
            user_id: userId,
            ...comment,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };
        comments.push(newComment);
        await saveComments(comments);
        return newComment.comment_id;
    } catch (error) {
        console.error('댓글 생성 오류:', error);
        throw error;
    }
};

// 댓글 수정 함수
const updateComment = async (content, commentId) => {
    try {
        const comments = await getComments();
        const targetIndex = comments.findIndex(
            (comment) => comment.comment_id === commentId
        );
        if (targetIndex === -1) {
            return null;
        }
        const updatedComment = {
            user_id: comments[targetIndex].user_id,
            ...comments[targetIndex],
            content,
            updated_at: new Date().toISOString(),
        };
        comments[targetIndex] = updatedComment;
        await saveComments(comments);
        return updatedComment;
    } catch (error) {
        console.error('댓글 수정 오류:', error);
        throw error;
    }
};

// 페이지네이션된 댓글 목록 조회 함수
const getPaginatedComments = async (postId, page, limit) => {
    try {
        const comments = await getComments();
        const paginatedComments = comments
            .filter((comment) => comment.post_id === Number(postId))
            .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            .slice((page - 1) * limit, page * limit);
        return paginatedComments;
    } catch (error) {
        console.error('댓글 데이터 조회 오류:', error);
        throw error;
    }
};

module.exports = {
    getComments,
    getCommentById,
    saveComments,
    createComment,
    updateComment,
    getPaginatedComments,
};
