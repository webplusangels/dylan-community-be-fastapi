const fs = require('fs').promises;
const path = require('path');

const postsDataPath = path.join(__dirname, '../data/posts.json');

// 포스트 데이터를 읽어오는 함수
const getPosts = async () => {
    try {
        const data = await fs.readFile(postsDataPath, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        console.error('JSON 파일 읽기 오류:', error);
        throw error;
    }
};

// 포스트 데이터를 저장하는 함수
const savePosts = async (posts) => {
    try {
        await fs.writeFile(
            postsDataPath,
            JSON.stringify(posts, null, 2),
            'utf-8'
        );
    } catch (error) {
        console.error('JSON 파일 쓰기 오류:', error);
        throw error;
    }
};

// ID로 단일 포스트 조회 함수
const getPostById = async (id) => {
    try {
        const posts = await getPosts();
        const postData = posts.find((post) => post.post_id === Number(id));
        if (!postData) {
            return null;
        }
        return postData;
    } catch (error) {
        console.error('포스트 데이터 조회 오류:', error);
        throw error;
    }
};

// 포스트 생성 함수
const createPost = async (post, userId) => {
    try {
        const posts = await getPosts();
        const newPost = {
            post_id: posts.length + 1,
            user_id: userId,
            ...post,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };
        posts.push(newPost);
        await savePosts(posts);
        return newPost.post_id;
    } catch (error) {
        console.error('포스트 생성 오류:', error);
        throw error;
    }
};

// 페이지네이션된 포스트 목록 조회 함수
const getPaginatedPosts = async (page, limit) => {
    try {
        const posts = await getPosts();
        // 가장 최근 포스트가 맨 위에 오도록 정렬
        posts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        // 페이지네이션
        const startIndex = (page - 1) * limit;
        const endIndex = page * limit;
        return posts.slice(startIndex, endIndex);
    } catch (error) {
        console.error('포스트 데이터 조회 오류:', error);
        throw error;
    }
};

// ID로 포스트 수정 함수
const updatePostById = async (id, post) => {
    try {
        const posts = await getPosts();
        const targetIndex = posts.findIndex((p) => p.post_id === Number(id));
        if (targetIndex === -1) {
            return null;
        }
        const updatedPost = {
            ...posts[targetIndex],
            ...post,
            updated_at: new Date().toISOString(),
        };
        posts[targetIndex] = updatedPost;
        await savePosts(posts);
        return updatedPost;
    } catch (error) {
        console.error('포스트 수정 오류:', error);
        throw error;
    }
};

// ID로 포스트 삭제 함수
const deletePostById = async (id) => {
    try {
        const posts = await getPosts();
        const targetIndex = posts.findIndex((p) => p.post_id === Number(id));
        if (targetIndex === -1) {
            return null;
        }
        const deletedPost = posts.splice(targetIndex, 1)[0];
        await savePosts(posts);
        return deletedPost;
    } catch (error) {
        console.error('포스트 삭제 오류:', error);
        throw error;
    }
};

// 포스트 메타 정보 조회 함수
const getPostMetaById = async (id) => {
    try {
        const postData = await getPostById(id);
        if (!postData) {
            return null;
        }
        const meta = {
            views: postData.views,
            likes: postData.likes,
            comments_count: postData.comments_count, // TODO: 동적 업데이트
        };
        return meta;
    } catch (error) {
        console.error('포스트 메타 정보 조회 오류:', error);
        throw error;
    }
};

// 포스트 메타 정보 업데이트 함수
// TODO: 데이터베이스 업데이트하면 이 함수도 수정해야 함
const updatePostMetaById = async (id, meta) => {
    try {
        const posts = await getPosts();
        const targetIndex = posts.findIndex(
            (post) => post.post_id === Number(id)
        );
        if (targetIndex === -1) {
            return null;
        }
        const updatedPost = {
            ...posts[targetIndex],
            ...meta,
        };
        posts[targetIndex] = updatedPost;
        await savePosts(posts);
        return updatedPost;
    } catch (error) {
        console.error('포스트 메타 정보 업데이트 오류:', error);
        throw error;
    }
};

module.exports = {
    getPostById,
    createPost,
    getPaginatedPosts,
    updatePostById,
    deletePostById,
    getPostMetaById,
    updatePostMetaById,
};
