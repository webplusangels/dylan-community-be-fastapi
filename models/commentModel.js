/* eslint-disable camelcase */
const { v4: uuidv4 } = require('uuid');
const { getById, createRecord, formatDate } = require('../config/utils');
const { query } = require('../db/db');

// 댓글 ID로 단일 댓글 조회 함수
const getCommentById = async (id) => {
    return getById('comments', id);
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
        const existingComment = await getById('comments', id);
        const sql = `
            UPDATE comments
            SET content = ?, updated_at = ?
            WHERE id = ?
        `;
        await query(sql, [
            content || existingComment.content,
            formatDate(new Date()),
            id,
        ]);
    } catch (error) {
        console.error('댓글 수정 오류:', error);
        throw error;
    }
};

// 페이지네이션된 댓글 목록 조회 함수
const getPaginatedComments = async (postId, lastCreatedAt, limit) => {
    try {
        const sql = `
            SELECT comment_id, post_id, user_id, content, created_at, updated_at
            FROM comments
            WHERE post_id = ? AND created_at > ?
            ORDER BY created_at ASC
            LIMIT ?`;
        const rows = await query(sql, [
            postId,
            formatDate(lastCreatedAt),
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
            WHERE id = ?
        `;
        await query(sql, [id]);
    } catch (error) {
        console.error('댓글 삭제 오류:', error);
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
            WHERE id = ?
        `;
        await query(updateSql, [comments_count, postId]);
        const existingPost = await getById('posts', postId);
        return { ...existingPost, comments_count };
    } catch (error) {
        console.error('포스트 댓글 수 정보 업데이트 오류:', error);
        throw error;
    }
};

module.exports = {
    getCommentById,
    createComment,
    updateCommentById,
    getPaginatedComments,
    deleteCommentById,
    updateCommentsCountById,
};
