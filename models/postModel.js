/* eslint-disable camelcase */
const { v4: uuidv4 } = require('uuid');
const { getById, createRecord, formatDate } = require('../utils/utils');
const { query } = require('../utils/dbUtils');

// ID로 포스트 조회 함수
const getPostById = async (id) => {
    try {
        const sql = `
            SELECT posts.*, users.nickname AS author, users.profile_image_path AS profile_image
            FROM posts
            JOIN users ON posts.user_id = users.user_id
            WHERE posts.post_id = ?
        `;
        const rows = await query(sql, [id]);
        if (rows.length !== 1) {
            throw new Error('포스트를 찾을 수 없습니다.');
        }

        return rows[0];
    } catch (error) {
        console.error('포스트 데이터 조회 오류:', error.message);
        throw error;
    }
};

// id로 포스트 id 조회
const getPostIdById = async (id) => {
    try {
        const sql = `
            SELECT post_id
            FROM posts
            WHERE id = ?
        `;
        const rows = await query(sql, [id]);
        if (rows.length !== 1) {
            throw new Error('포스트를 찾을 수 없습니다.');
        }
        return rows[0];
    } catch (error) {
        console.error('포스트 데이터 조회 오류:', error.message);
        throw error;
    }
};

// 포스트 생성 함수
const createPost = async (post, userId) => {
    const now = new Date();
    const formattedDate = formatDate(now);

    const data = {
        post_id: uuidv4(),
        user_id: userId,
        title: post.title,
        content: post.content,
        image_path: post.image_path || null,
        views: post.views || 0,
        likes: post.likes || 0,
        comments_count: post.comments_count || 0,
        created_at: formattedDate,
        updated_at: formattedDate,
    };
    return createRecord('posts', data);
};

// 페이지네이션된 포스트 목록 조회 함수
const getPaginatedPosts = async (lastCreatedAt, limit) => {
    try {
        const sql = `
            SELECT 
                posts.post_id, 
                posts.user_id, 
                posts.title, 
                posts.content, 
                posts.image_path, 
                posts.views, 
                posts.likes, 
                posts.comments_count, 
                posts.created_at, 
                posts.updated_at,
                users.nickname AS author,
                users.profile_image_path AS profile_image
            FROM posts
            JOIN users ON posts.user_id = users.user_id
            WHERE posts.created_at < ?
            ORDER BY posts.created_at DESC
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
        const existingPost = await getById('posts', postId, 'post_id');
        const sql = `
            UPDATE posts
            SET title = ?, content = ?, image_path = ?, updated_at = ?
            WHERE post_id = ?
        `;
        await query(sql, [
            post.title || existingPost.title,
            post.content || existingPost.content,
            post.image_path || existingPost.image_path,
            formatDate(new Date()),
            postId,
        ]);
        return postId;
    } catch (error) {
        console.error('포스트 수정 오류:', error.message);
        throw error;
    }
};

// ID로 포스트 삭제 함수
const deletePostById = async (id) => {
    try {
        // likes 테이블에서 삭제
        const deleteLikesSql = `
            DELETE FROM likes
            WHERE post_id = ?
        `;
        await query(deleteLikesSql, [id]);
        // comments 테이블에서 삭제
        const deleteCommentsSql = `
            DELETE FROM comments
            WHERE post_id = ?
        `;
        await query(deleteCommentsSql, [id]);
        const deletePostssql = `
            DELETE FROM posts
            WHERE post_id = ?
        `;
        await query(deletePostssql, [id]);
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
            WHERE post_id = ?
        `;
        const meta = await query(sql, [id]);
        return meta[0];
    } catch (error) {
        console.error('포스트 메타 정보 조회 오류:', error.message);
        throw error;
    }
};

// 포스트 조회수 정보 업데이트 함수
const updatePostViewById = async (id) => {
    try {
        const existingPost = await getById('posts', id, 'post_id');
        if (!existingPost) {
            throw new Error('포스트를 찾을 수 없습니다.');
        }

        const newViews = existingPost.views + 1;
        const sql = `
            UPDATE posts
            SET views = ?
            WHERE post_id = ?
        `;
        await query(sql, [newViews, id]);
    } catch (error) {
        console.error('포스트 조회수 정보 업데이트 오류:', error.message);
        throw error;
    }
};

// 포스트 좋아요 수 정보 업데이트 함수
const updatePostLikesById = async (postId) => {
    try {
        // 좋아요 수 계산 (likes 테이블에서 동적으로 계산)
        const sqlCountLikes = `
            SELECT COUNT(*) AS likeCount
            FROM likes
            WHERE post_id = ?
        `;
        const [result] = await query(sqlCountLikes, [postId]);
        const likes = result.likeCount;

        if (likes === undefined) {
            throw new Error('좋아요 수 계산 실패');
        }

        // 게시물 좋아요 수 업데이트
        const sqlUpdateLikes = `
            UPDATE posts
            SET likes = ?
            WHERE post_id = ?
        `;
        await query(sqlUpdateLikes, [likes, postId]);

        return likes; // 업데이트된 좋아요 수 반환
    } catch (error) {
        console.error('포스트 좋아요 수 업데이트 오류:', error.message);
        throw error;
    }
};

const updatePostCommentsCountById = async (postId) => {
    try {
        const sql = `
            SELECT COUNT(*) AS count
            FROM comments
            WHERE post_id = ?
        `;
        const [result] = await query(sql, [postId]);
        const comments_count = result.count;

        const updateSql = `
            UPDATE posts
            SET comments_count = ?
            WHERE post_id = ?
        `;
        await query(updateSql, [comments_count, postId]);
        return comments_count;
    } catch (error) {
        console.error('포스트 댓글 수 정보 업데이트 오류:', error.message);
        throw error;
    }
};

// 포스트 좋아요 버튼 클릭 함수
const toggleLike = async (postId, userId) => {
    try {
        const sqlCheck = `
            SELECT COUNT(*) AS count
            FROM likes
            WHERE post_id = ? AND user_id = ?
        `;
        const [result] = await query(sqlCheck, [postId, userId]);
        const isLike = result.count > 0;
        if (isLike) {
            const sqlDelete = `
                DELETE FROM likes
                WHERE post_id = ? AND user_id = ?
            `;
            await query(sqlDelete, [postId, userId]);
        } else {
            const sqlInsert = `
                INSERT INTO likes (post_id, user_id)
                VALUES (?, ?)
            `;
            await query(sqlInsert, [postId, userId]);
        }
        const updatedLikes = await updatePostLikesById(postId);
        return { isLike: !isLike, updatedLikes }; // 상태와 좋아요 수 반환
    } catch (error) {
        console.error('포스트 좋아요 토글 오류:', error.message);
        throw error;
    }
};

const getLikeStatus = async (postId, userId) => {
    try {
        const sql = `
            SELECT COUNT(*) AS count
            FROM likes
            WHERE post_id = ? AND user_id = ?
        `;
        const [result] = await query(sql, [postId, userId]);
        const isLike = result.count > 0;
        return { isLike };
    } catch (error) {
        console.error('포스트 좋아요 상태 조회 오류:', error.message);
        throw error;
    }
};

module.exports = {
    getPostById,
    getPostIdById,
    createPost,
    getPaginatedPosts,
    updatePostById,
    deletePostById,
    getPostMetaById,
    updatePostViewById,
    updatePostLikesById,
    updatePostCommentsCountById,
    toggleLike,
    getLikeStatus,
};
