/* eslint-disable camelcase */
const { v4: uuidv4 } = require('uuid');
const { getById, createRecord, formatDate } = require('../utils/utils');
const { query } = require('../utils/dbUtils');

// 댓글 ID로 단일 댓글 조회 함수
const getCommentById = async (id) => {
    return getById('comments', id, 'comment_id');
};

const getCommentsByPostId = async (postId) => {
    try {
        const sql = `
            SELECT 
                comments.comment_id, 
                comments.post_id, 
                comments.user_id, 
                comments.content, 
                comments.created_at, 
                comments.updated_at,
                users.nickname AS author,
                users.profile_image_path AS profile_image
            FROM comments
            JOIN users ON comments.user_id = users.user_id
            WHERE comments.post_id = ?
            ORDER BY created_at DESC
        `;
        const rows = await query(sql, [postId]);
        return rows;
    } catch (error) {
        console.error('댓글 데이터 조회 오류:', error.message);
        throw error;
    }
};

// 댓글 생성 함수
const createComment = async (comment, postId, userId) => {
    const data = {
        comment_id: uuidv4(),
        post_id: postId,
        user_id: userId,
        content: comment.content,
        created_at: formatDate(new Date()),
        updated_at: formatDate(new Date()),
    };
    return createRecord('comments', data);
};

// 댓글 수정 함수
const updateCommentById = async (content, id) => {
    try {
        const existingComment = await getById('comments', id, 'comment_id');
        const sql = `
            UPDATE comments
            SET content = ?, updated_at = ?
            WHERE comment_id = ?
        `;
        await query(sql, [
            content || existingComment.content,
            formatDate(new Date()),
            id,
        ]);
        return { ...existingComment, content };
    } catch (error) {
        console.error('댓글 수정 오류:', error.message);
        throw error;
    }
};

// 페이지네이션된 댓글 목록 조회 함수
const getPaginatedComments = async (
    postId,
    limit = 10,
    lastCreatedAt = new Date()
) => {
    try {
        const sql = `
            SELECT 
                comments.comment_id, 
                comments.post_id, 
                comments.user_id, 
                comments.content, 
                comments.created_at, 
                comments.updated_at,
                users.nickname AS author,
                users.profile_image_path AS profile_image
            FROM comments
            JOIN users ON comments.user_id = users.user_id
            WHERE comments.post_id = ? AND (comments.created_at < ? OR ? IS NULL)
            ORDER BY created_at DESC
            LIMIT ?`;
        const rows = await query(sql, [
            postId,
            formatDate(lastCreatedAt),
            lastCreatedAt || null,
            limit,
        ]);
        return rows;
    } catch (error) {
        console.error('댓글 데이터 조회 오류:', error.message);
        throw error;
    }
};

// 댓글 삭제 함수
const deleteCommentById = async (id) => {
    try {
        const sql = `
            DELETE FROM comments
            WHERE comment_id = ?
        `;
        await query(sql, [id]);
    } catch (error) {
        console.error('댓글 삭제 오류:', error.message);
        throw error;
    }
};

// 포스트 댓글 수 정보 업데이트 함수
const updateCommentsCountById = async (postId) => {
    try {
        const sql = `
            SELECT COUNT(*) AS count
            FROM comments
            WHERE post_id = ?
        `;
        const rows = await query(sql, [postId]);
        const comments_count = rows[0].count;

        const updateSql = `
            UPDATE posts
            SET comments_count = ?
            WHERE post_id = ?
        `;
        await query(updateSql, [comments_count, postId]);
        const existingPost = await getById('posts', postId, 'post_id');
        return { ...existingPost, comments_count };
    } catch (error) {
        console.error('포스트 댓글 수 정보 업데이트 오류:', error.message);
        throw error;
    }
};

module.exports = {
    getCommentById,
    getCommentsByPostId,
    createComment,
    updateCommentById,
    getPaginatedComments,
    deleteCommentById,
    updateCommentsCountById,
};
