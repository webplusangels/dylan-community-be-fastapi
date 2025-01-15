const bcrypt = require('bcrypt');
const userModel = require('../models/userModel');
const { setSessionUser } = require('../utils/utils');
const { getUploadedFileUrl } = require('../utils/uploadUtils');
const { ERROR_MESSAGES } = require('../config/constants');
const { UnauthorizedError } = require('../utils/customError');

// 세션 확인
const getSession = (req, res) => {
    try {
        // 세션 유효성 확인
        if (!req.session || !req.session.user) {
            res.status(401).json({
                message: '세션이 만료되었거나 로그인이 필요합니다.',
            });
            return;
        }

        // 세션 정보 반환
        const { user } = req.session;
        res.status(200).json(user);
    } catch (error) {
        console.error('세션 정보 조회 오류:', error.message);
        res.status(500).json({ message: '서버 오류가 발생했습니다.' });
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

        setSessionUser(req, newUser);

        res.status(201).json({ message: '사용자 등록 성공' });
    } catch (err) {
        console.error('사용자 등록 오류:', err);
        next(err);
    }
};

const getProfile = async (req, res, next) => {
    const { user } = req.session;
    console.log('user:', user);
    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    try {
        req.session.touch(); // 세션 만료 시간 갱신

        const userProfile = await userModel.getUserByEmail(user.email);
        if (!userProfile) {
            res.status(404).json({
                message: '사용자 프로필을 찾을 수 없습니다.',
            });
            return;
        }

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

    if (!nickname) {
        res.status(400).json({ message: '입력 항목 누락' });
        return;
    }

    try {
        const updatedUser = await userModel.updateUserProfile(user.user_id, {
            nickname,
            profileImagePath,
        });

        // 세션 사용자 정보 업데이트
        setSessionUser(req, updatedUser);

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
            throw new UnauthorizedError('로그인 실패');
        }

        // 세션 사용자 설정
        setSessionUser(req, user);

        res.status(200).json({
            message: '로그인 성공',
            user: req.session.user,
        });
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

    const passwordRegex =
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$/;
    if (!passwordRegex.test(password)) {
        res.status(400).json({
            message: '비밀번호 형식이 올바르지 않습니다.',
        });
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

// 프로필 이미지 업로드
const uploadProfileImage = async (req, res, next) => {
    try {
        const fileUrl = getUploadedFileUrl(req.file);
        res.status(200).json({ url: fileUrl });
    } catch (err) {
        console.error('이미지 업로드 오류:', err);
        next(err);
    }
};

module.exports = {
    getSession,
    getProfile,
    updateProfile,
    addUser,
    loginUser,
    logoutUser,
    deleteProfile,
    resetPassword,
    uploadProfileImage,
};
