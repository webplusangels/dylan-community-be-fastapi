const fs = require('fs').promises;
const path = require('path');

// id 추가를 위한 임시 uuid 모듈
const { v4: uuidv4 } = require('uuid');

const usersDataPath = path.join(__dirname, '../data/users.json');

// 사용자 데이터를 읽어오는 함수
const getUsers = async () => {
    try {
        const data = await fs.readFile(usersDataPath, 'utf-8');
        return JSON.parse(data);
    } catch (error) {
        console.error('JSON 파일 읽기 오류:', error);
        throw error;
    }
};

// 필수 데이터 중복 확인 함수
const isDuplicateUser = async (email, nickname, targetId = null) => {
    const users = await getUsers();
    let emailExists = false;
    let nicknameExists = false;
    if (!email) {
        emailExists = users.some((u) => u.email === email && u.id !== targetId);
    }

    nicknameExists = users.some(
        (u) => u.nickname === nickname && u.id !== targetId
    );
    return { emailExists, nicknameExists };
};

// 사용자 데이터를 추가하는 함수
const addUser = async (user) => {
    try {
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

        const timestamp = new Date().toISOString();
        const newUser = {
            user_id: uuidv4(),
            ...user,
            created_at: timestamp,
            updated_at: timestamp,
        };
        const users = await getUsers();
        users.push(newUser);
        await fs.writeFile(usersDataPath, JSON.stringify(users, null, 2));
        return newUser;
    } catch (error) {
        console.error('JSON 파일 쓰기 오류:', error);
        throw error;
    }
};

// 이메일로 사용자 데이터를 가져오는 함수
const getUserByEmail = async (email) => {
    try {
        const users = await getUsers();
        const userData = users.find((user) => user.email === email);
        if (!userData) {
            throw new Error('사용자를 찾을 수 없습니다.');
        }
        return userData;
    } catch (error) {
        console.error('사용자 데이터 조회 오류:', error);
        throw error;
    }
};

// 사용자 패스워드를 업데이트하는 함수
const updateUserPassword = async (email, hashedPassword) => {
    try {
        const users = await getUsers();
        const userData = users.find((user) => user.email === email);
        if (!userData) {
            throw new Error('사용자를 찾을 수 없습니다.');
        }
        userData.password = hashedPassword;
        await fs.writeFile(usersDataPath, JSON.stringify(users, null, 2));
    } catch (error) {
        console.error('패스워드 업데이트 오류:', error);
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

        const users = await getUsers();
        const user = users.find((u) => u.id === id);
        if (!user) {
            throw new Error('사용자를 찾을 수 없습니다.');
        }
        user.nickname = updatedData.nickname;
        user.profileImagePath = updatedData.profileImagePath;
        user.updatedAt = new Date().toISOString();
        await fs.writeFile(usersDataPath, JSON.stringify(users, null, 2));
        return user;
    } catch (error) {
        console.error('프로필 업데이트 오류:', error);
        throw error;
    }
};

// 사용자 ID로 사용자 데이터를 삭제하는 함수
const deleteUserById = async (id) => {
    try {
        const users = await getUsers();
        const userIndex = users.findIndex((u) => u.id === id);
        if (userIndex === -1) {
            throw new Error('사용자를 찾을 수 없습니다.');
        }
        users.splice(userIndex, 1);
        await fs.writeFile(usersDataPath, JSON.stringify(users, null, 2));
    } catch (error) {
        console.error('사용자 삭제 오류:', error);
        throw error;
    }
};

module.exports = {
    getUsers,
    addUser,
    getUserByEmail,
    updateUserPassword,
    updateUserProfile,
    deleteUserById,
};
