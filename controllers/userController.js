const bcrypt = require('bcrypt');
const userModel = require('../models/userModel');
const { ERROR_MESSAGES } = require('../config/constants');

// 사용자 목록 조회
const getUsers = async (req, res, next) => {
    try {
        const users = await userModel.getUsers();
        res.status(200).json(users);
    } catch (err) {
        console.error('사용자 목록 조회 오류:', err);
        next(err);
    }
};

// 세션 확인
const getSession = (req, res, next) => {
    try {
        if (!req.session.user) {
            res.json({ isAuthenticated: false });
            return;
        }
        res.json({ isAuthenticated: true });
    } catch (err) {
        console.error('세션 확인 오류:', err);
        next(err);
    }
};

// 사용자 인증
const authenticateUser = async (email, password) => {
    try {
        const user = await userModel.getUserByEmail(email);
        if (!user) {
            return null;
        }

        const isValid = await bcrypt.compare(password, user.password);
        if (!isValid) {
            return null;
        }

        return user;
    } catch (error) {
        console.error('사용자 인증 오류:', error);
        throw error;
    }
};

// 사용자 추가
const addUser = async (req, res, next) => {
    const { email, nickname, password, profileImagePath } = req.body;

    // 입력 데이터 검증
    if (!email || !nickname || !password) {
        res.status(400).json({ message: '필수 입력 항목이 누락되었습니다.' });
        return;
    }

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        const user = {
            email,
            nickname,
            password: hashedPassword,
            profileImagePath: profileImagePath || null,
        };

        const newUser = await userModel.addUser(user);

        req.session.user = {
            user_id: newUser.user_id,
            email: newUser.email,
            nickname: newUser.nickname,
        };

        res.status(201).json({ message: '사용자 등록 성공' });
    } catch (err) {
        console.error('사용자 등록 오류:', err);
        next(err);
    }
};

const getProfile = async (req, res, next) => {
    const { user } = req.session;

    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    try {
        const userProfile = await userModel.getUserByEmail(user.email);
        res.status(200).json(userProfile);
    } catch (err) {
        console.error('프로필 조회 오류:', err);
        next(err);
    }
};

const updateProfile = async (req, res, next) => {
    const { user } = req.session;
    const { nickname, profileImagePath } = req.body;

    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    if (!nickname || !profileImagePath) {
        res.status(400).json({ message: '입력 항목 누락' });
        return;
    }

    try {
        const updatedUser = await userModel.updateUserProfile(user.id, {
            nickname,
            profileImagePath,
        });

        // 세션 사용자 정보 업데이트
        req.session.user = {
            id: updatedUser.id,
            email: updatedUser.email,
            nickname: updatedUser.nickname,
        };

        // 변경된 세션 저장 후 응답
        req.session.save((err) => {
            if (err) {
                console.error('세션 저장 오류:', err);
                res.status(500).json({
                    message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
                });
                return;
            }
            res.status(200).json({ message: '프로필 업데이트 성공' });
        });
    } catch (err) {
        console.error('프로필 업데이트 오류:', err);
        next(err);
    }
};

// 사용자 삭제
const deleteProfile = async (req, res, next) => {
    const { user } = req.session;

    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    try {
        await userModel.deleteUserById(user.id);

        req.session.destroy((err) => {
            if (err) {
                console.error('세션 무효화 오류:', err);
                res.status(500).json({
                    message: ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
                });
                return;
            }
            res.clearCookie('connect.sid'); // 클라이언트 측 세션 쿠키 삭제
            res.status(200).json({ message: '사용자 삭제 성공' });
        });
    } catch (err) {
        console.error('사용자 삭제 오류:', err);
        next(err);
    }
};

// 사용자 로그인
const loginUser = async (req, res, next) => {
    const { email, password } = req.body;

    if (!email || !password) {
        res.status(400).json({ message: '필수 입력 항목 누락' });
        return;
    }

    try {
        const user = await authenticateUser(email, password);
        if (!user) {
            res.status(401).json({
                meesage: ERROR_MESSAGES.INVALID_CREDENTIALS,
            });
            return;
        }

        // 세션 사용자 설정
        req.session.user = {
            user_id: user.user_id,
            email: user.email,
            nickname: user.nickname,
        };

        res.status(200).json({ message: '로그인 성공' });
    } catch (err) {
        console.error('로그인 오류:', err);
        next(err);
    }
};

// 사용자 로그아웃
const logoutUser = (req, res, next) => {
    try {
        // 세션 무효화
        req.session.destroy((err) => {
            if (err) {
                throw err;
            }
            res.clearCookie('connect.sid'); // 클라이언트 측 세션 쿠키 삭제
            res.status(200).json({ message: '로그아웃 성공' });
        });
    } catch (err) {
        console.error('로그아웃 오류:', err);
        next(err);
    }
};

// 패스워드 재설정
const resetPassword = async (req, res, next) => {
    const { password } = req.body;

    // 세션에서 사용자 정보 가져오기
    const { user } = req.session;

    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    if (!password) {
        res.status(400).json({ message: '필수 입력 항목 누락' });
        return;
    }

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        await userModel.updateUserPassword(user.email, hashedPassword);

        // 세션 무효화
        req.session.destroy((err) => {
            if (err) {
                console.error('세션 무효화 오류:', err);
                next(err);
                return;
            }
            res.clearCookie('connect.sid'); // 클라이언트 측 세션 쿠키 삭제
            res.status(200).json({ message: '패스워드 재설정 성공' });
        });
    } catch (err) {
        console.error('패스워드 재설정 오류:', err);
        next(err);
    }
};

module.exports = {
    getUsers,
    getSession,
    getProfile,
    updateProfile,
    addUser,
    loginUser,
    logoutUser,
    deleteProfile,
    resetPassword,
};
