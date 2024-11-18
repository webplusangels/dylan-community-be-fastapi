/* eslint-disable camelcase */
const { v4: uuidv4 } = require('uuid');
const { getById, createRecord, formatDate } = require('../utils');
const { query } = require('../db');

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
        console.error('포스트 수정 오류:', error);
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
        console.error('포스트 삭제 오류:', error);
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
        console.error('포스트 메타 정보 조회 오류:', error);
        throw error;
    }
};

// 포스트 메타 정보 업데이트 함수
// TODO: 데이터베이스 업데이트하면 이 함수도 수정해야 함
const updatePostMetaById = async (id, meta) => {
    try {
        const sql = `
            UPDATE posts
            SET views = ?, likes = ?, comments_count = ?
            WHERE id = ?
        `;
        const existingPost = await getById('posts', id);
        const updatedMeta = {
            views: meta.views !== undefined ? meta.views : existingPost.views,
            likes: meta.likes !== undefined ? meta.likes : existingPost.likes,
            comments_count:
                meta.comments_count !== undefined
                    ? meta.comments_count
                    : existingPost.comments_count,
        };
        await query(sql, [
            updatedMeta.views,
            updatedMeta.likes,
            updatedMeta.comments_count,
            updatedMeta.updated_at,
            id,
        ]);
        return { ...existingPost, ...updatedMeta };
    } catch (error) {
        console.error('포스트 메타 정보 업데이트 오류:', error);
        throw error;
    }
};

module.exports = {
    createPost,
    getPaginatedPosts,
    updatePostById,
    deletePostById,
    getPostMetaById,
    updatePostMetaById,
};
