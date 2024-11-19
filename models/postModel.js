/* eslint-disable camelcase */
const { v4: uuidv4 } = require('uuid');
const { getById, createRecord, formatDate } = require('../utils/utils');
const { query } = require('../utils/dbUtils');

// 포스트 생성 함수
const createPost = async (post, userId) => {
    const data = {
        post_id: uuidv4(),
        user_id: userId,
        title: post.title,
        content: post.content,
        image_path: post.image_path || null,
        views: post.views || 0,
        likes: post.likes || 0,
        comments_count: post.comments_count || 0,
        created_at: formatDate(new Date()),
        updated_at: formatDate(new Date()),
    };
    return createRecord('posts', data);
};

// 페이지네이션된 포스트 목록 조회 함수
const getPaginatedPosts = async (lastCreatedAt, limit) => {
    try {
        const sql = `
            SELECT post_id, user_id, title, content, image_path, views, likes, comments_count, created_at, updated_at
            FROM posts
            WHERE created_at < ?
            ORDER BY created_at DESC
            LIMIT ?`;
        const rows = await query(sql, [formatDate(lastCreatedAt), limit]);
        return rows;
    } catch (error) {
        console.error('포스트 데이터 조회 오류:', error.message);
        throw error;
    }
};

// ID로 포스트 수정 함수
const updatePostById = async (post, postId) => {
    try {
        const existingPost = await getById('posts', postId);
        const sql = `
            UPDATE posts
            SET title = ?, content = ?, image_path = ?, updated_at = ?
            WHERE id = ?
        `;
        await query(sql, [
            post.title || existingPost.title,
            post.content || existingPost.content,
            post.image_path || existingPost.image_path,
            formatDate(new Date()),
            postId,
        ]);
    } catch (error) {
        console.error('포스트 수정 오류:', error.message);
        throw error;
    }
};

// ID로 포스트 삭제 함수
const deletePostById = async (id) => {
    try {
        const sql = `
            DELETE FROM posts
            WHERE id = ?
        `;
        await query(sql, [id]);
    } catch (error) {
        console.error('포스트 삭제 오류:', error.message);
        throw error;
    }
};

// 포스트 메타 정보 조회 함수
const getPostMetaById = async (id) => {
    try {
        const sql = `
            SELECT views, likes, comments_count
            FROM posts
            WHERE id = ?
        `;
        const meta = await query(sql, [id]);
        return meta[0];
    } catch (error) {
        console.error('포스트 메타 정보 조회 오류:', error.message);
        throw error;
    }
};

// 포스트 조회수 정보 업데이트 함수
const updatePostViewById = async (id, views) => {
    try {
        const sql = `
            UPDATE posts
            SET views = ?
            WHERE id = ?
        `;
        const existingPost = await getById('posts', id);
        await query(sql, [views || existingPost.views, id]);
        return { ...existingPost, views };
    } catch (error) {
        console.error('포스트 조회수 정보 업데이트 오류:', error.message);
        throw error;
    }
};

// 포스트 좋아요 수 정보 업데이트 함수
const updatePostLikesById = async (id, likes) => {
    try {
        const sql = `
            UPDATE posts
            SET likes = ?
            WHERE id = ?
        `;
        const existingPost = await getById('posts', id);
        await query(sql, [likes || existingPost.likes, id]);
        return { ...existingPost, likes };
    } catch (error) {
        console.error('포스트 좋아요 수 정보 업데이트 오류:', error.message);
        throw error;
    }
};

module.exports = {
    createPost,
    getPaginatedPosts,
    updatePostById,
    deletePostById,
    getPostMetaById,
    updatePostViewById,
    updatePostLikesById,
};
