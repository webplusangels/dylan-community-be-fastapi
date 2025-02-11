const jwt = require('jsonwebtoken');

// JWT 생성
const generateToken = (user) => {
    return jwt.sign(
        {
            id: user.id,
            user_id: user.user_id,
            email: user.email,
            nickname: user.nickname,
            profileImagePath: user.profile_image_path,
        },
        process.env.JWT_SECRET,
        {
            expiresIn: Number(process.env.JWT_EXPIRES_IN) || 3600,
        }
    );
};

// JWT 검증
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];
    if (!token) {
        res.status(401).json({ message: '로그인이 필요합니다.' });
        return;
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            res.status(403).json({ message: '토큰이 만료되었습니다.' });
            return;
        }
        req.user = user;
        next();
    });
};

module.exports = { generateToken, authenticateToken };
