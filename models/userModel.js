const { v4: uuidv4 } = require('uuid');
const { getById, createRecord, formatDate } = require('../utils/utils');
const { query } = require('../utils/dbUtils');

// 필수 데이터 중복 확인 함수
const isDuplicateUser = async (email, nickname, userId = null) => {
    let emailExists = false;
    let nicknameExists = false;

    // 이메일 중복 확인
    if (email) {
        const emailSql = `
            SELECT COUNT(*) AS count
            FROM users
            WHERE email = ? ${userId ? 'AND id != ?' : ''}
        `;
        const emailParams = userId ? [email, userId] : [email];
        const emailResult = await query(emailSql, emailParams);
        emailExists = emailResult[0].count > 0;
    }

    // 닉네임 중복 확인
    const nicknameSql = `
        SELECT COUNT(*) AS count
        FROM users
        WHERE nickname = ? ${userId ? 'AND user_id != ?' : ''}
    `;
    const nicknameParams = userId ? [nickname, userId] : [nickname];
    const nicknameResult = await query(nicknameSql, nicknameParams);
    nicknameExists = nicknameResult[0].count > 0;

    return { emailExists, nicknameExists };
};

// 사용자 데이터를 추가하는 함수
const addUser = async (user) => {
    // 이메일, 닉네임 중복 확인
    const { emailExists, nicknameExists } = await isDuplicateUser(
        user.email,
        user.nickname
    );
    if (emailExists) {
        throw new Error('이미 사용 중인 이메일입니다.');
    }
    if (nicknameExists) {
        throw new Error('이미 사용 중인 닉네임입니다.');
    }
    const data = {
        user_id: uuidv4(),
        email: user.email,
        nickname: user.nickname,
        password: user.password,
        profile_image_path: user.profileImagePath || null,
        created_at: formatDate(new Date()),
        updated_at: formatDate(new Date()),
    };
    const userId = await createRecord('users', data);
    return { ...data, id: userId };
};

// 이메일로 사용자 데이터를 가져오는 함수
const getUserByEmail = async (email) => {
    try {
        const sql = `
            SELECT id, user_id, email, nickname, password, profile_image_path, created_at, updated_at
            FROM users
            WHERE email = ?
        `;
        const rows = await query(sql, [email]);
        if (!rows.length) {
            throw new Error('사용자를 찾을 수 없습니다.');
        }
        rows[0].profile_image_path = rows[0].profile_image_path || null;
        return rows[0];
    } catch (error) {
        console.error('사용자 데이터 조회 오류:', error.message);
        throw error;
    }
};

// 사용자 패스워드를 업데이트하는 함수
const updateUserPassword = async (email, hashedPassword) => {
    try {
        const userData = await getUserByEmail(email);
        userData.password = hashedPassword;
        const sql = `
            UPDATE users
            SET password = ?
            WHERE email = ?
        `;
        await query(sql, [hashedPassword, email]);
    } catch (error) {
        console.error('패스워드 업데이트 오류:', error.message);
        throw error;
    }
};

// 사용자 프로필을 업데이트하는 함수
const updateUserProfile = async (id, updatedData) => {
    try {
        const { nicknameExists } = await isDuplicateUser(
            null,
            updatedData.nickname,
            id
        );
        if (nicknameExists) {
            throw new Error('이미 사용 중인 닉네임입니다.');
        }

        const sql = `
            UPDATE users
            SET nickname = ?, profile_image_path = ?, updated_at = ?
            WHERE user_id = ?
        `;
        await query(sql, [
            updatedData.nickname,
            updatedData.profileImagePath,
            formatDate(new Date()),
            id,
        ]);

        return getById('users', id, 'user_id');
    } catch (error) {
        console.error('프로필 업데이트 오류:', error.message);
        throw error;
    }
};

// 사용자 ID로 사용자 데이터를 삭제하는 함수
const deleteUserById = async (id) => {
    try {
        // likes 테이블에서 삭제
        const deleteLikesSql = `
            DELETE FROM likes
            WHERE user_id = ?
        `;
        await query(deleteLikesSql, [id]);
        // comments 테이블에서 삭제
        const deleteCommentsSql = `
            DELETE FROM comments
            WHERE user_id = ?
        `;
        await query(deleteCommentsSql, [id]);
        // posts 테이블에서 삭제
        const deletePostsSql = `
            DELETE FROM posts
            WHERE user_id = ?
        `;
        await query(deletePostsSql, [id]);
        // users 테이블에서 삭제
        const deleteUsersSql = `
            DELETE FROM users
            WHERE user_id = ?
        `;
        await query(deleteUsersSql, [id]);
    } catch (error) {
        console.error('사용자 삭제 오류:', error.message);
        throw error;
    }
};

module.exports = {
    addUser,
    getUserByEmail,
    updateUserPassword,
    updateUserProfile,
    deleteUserById,
};
