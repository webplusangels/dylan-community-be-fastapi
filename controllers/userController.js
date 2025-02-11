/* eslint-disable camelcase */
const bcrypt = require('bcrypt');
const userModel = require('../models/userModel');
const { getUploadedFileUrl } = require('../utils/uploadUtils');
const { generateToken } = require('../utils/jwt');
const { UnauthorizedError, ConflictError } = require('../utils/customError');
const { deleteProfileImage } = require('../utils/uploadUtils');

// 세션 확인
const getSession = (req, res) => {
    try {
        const { user } = req;
        if (!user) {
            res.status(401).json({ message: '로그인이 필요합니다.' });
            return;
        }
        res.status(200).json(user);
    } catch (error) {
        console.error('사용자 정보 조회 오류:', error.message);
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
        const token = generateToken(newUser);

        res.status(201).json({ message: '사용자 등록 성공', token });
    } catch (err) {
        console.error('사용자 등록 오류:', err);
        next(err);
    }
};

const getProfile = async (req, res, next) => {
    const { user } = req;
    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    try {
        const userProfile = await userModel.getUserByEmail(user.email);
        if (!userProfile) {
            res.status(404).json({
                message: '사용자 프로필을 찾을 수 없습니다.',
            });
            return;
        }
        const {
            user_id,
            email,
            nickname,
            profile_image_path,
            created_at,
            updated_at,
        } = userProfile;
        const filteredProfile = {
            user_id,
            email,
            nickname,
            profile_image_path,
            created_at,
            updated_at,
        };

        res.status(200).json(filteredProfile);
    } catch (err) {
        console.error('프로필 조회 오류:', err);
        next(err);
    }
};

const updateProfile = async (req, res, next) => {
    const { user } = req;
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

        res.status(200).json({ message: '프로필 업데이트 성공', updatedUser });
    } catch (err) {
        console.error('프로필 업데이트 오류:', err);
        next(err);
    }
};

// 사용자 삭제
const deleteProfile = async (req, res, next) => {
    const { user } = req;

    if (!user) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    try {
        // S3에 저장된 프로필 이미지 삭제
        if (user.profile_image_path) {
            await deleteProfileImage(
                user.user_id,
                user.profile_image_path.split('/').pop()
            );
        }
        await userModel.deleteUserById(user.user_id);
        console.log('탈퇴 성공');
        res.status(200).json({ message: '사용자 삭제 성공' });
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
        // 사용자가 있는지 확인
        const user = await authenticateUser(email, password);
        if (!user) {
            throw new UnauthorizedError('로그인 실패');
        }
        const token = generateToken(user);
        res.status(200).json({
            token,
        });
    } catch (err) {
        console.error('로그인 오류:', err);
        next(err);
    }
};

// 사용자 로그아웃
const logoutUser = (req, res, next) => {
    try {
        const { user } = req;
        res.status(200).json({ message: '로그아웃 성공', user });
    } catch (err) {
        console.error('로그아웃 오류:', err);
        next(err);
    }
};

// 패스워드 재설정
const resetPassword = async (req, res, next) => {
    const { password } = req.body;
    const { user } = req;

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

        res.status(200).json({ message: '패스워드 재설정 성공' });
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

// 이메일 중복 확인
const checkEmail = async (req, res, next) => {
    try {
        const { email } = req.body;
        const user = await userModel.getUserByEmail(email);

        if (user) {
            throw new ConflictError('이미 존재하는 이메일입니다.');
        }

        res.status(200).json({ message: '사용 가능한 이메일입니다.' });
    } catch (err) {
        if (err.message === '사용자를 찾을 수 없습니다.') {
            res.status(200).json({ message: '사용 가능한 이메일입니다.' });
        } else {
            console.error('이메일 중복 확인 오류:', err);
            next(err);
        }
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
    checkEmail,
};
