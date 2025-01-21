const express = require('express');
const dotenv = require('dotenv');
const session = require('express-session');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const errorHandler = require('./middlewares/errorHandler');
const authRouter = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const postRoutes = require('./routes/postRoutes');
const commentRoutes = require('./routes/commentRoutes');
const uploadRoutes = require('./routes/uploadRoutes');

dotenv.config(); // 로컬에서는 .env 파일 사용

const app = express();
const PORT = process.env.PORT || 8000;
if (
    !process.env.COOKIE_SECRET ||
    !process.env.DB_HOST ||
    !process.env.DB_USER
) {
    console.error('환경 변수 설정이 올바르지 않습니다. 서버를 종료합니다.');
    process.exit(1);
}

// 미들웨어 설정
app.use(express.json());
app.use(
    cors({
        origin: 'http://localhost:3000',
        credentials: true,
    })
);
app.use(
    '/api/',
    rateLimit({
        windowMs: 60 * 1000,
        max: 100,
        message: '잠시 후에 다시 시도하세요',
    })
); // 1분에 100회 요청 제한
app.use(
    /* 세션 설정 */
    session({
        secret: process.env.COOKIE_SECRET,
        resave: true,
        saveUninitialized: true,
        rolling: true, // 세션 요청 시 쿠키 유효시간 초기화
        cookie: {
            httpOnly: true,
            secure: false,
            maxAge: Number(process.env.SESSION_TIMEOUT) || 86400000,
        },
    })
);

// 라우터 등록
// 서브 라우터
const apiRouter = express.Router();
apiRouter.use('/auth', authRouter); // 인증 관련 API
apiRouter.use('/users', userRoutes); // 사용자 관련 API
apiRouter.use('/posts', postRoutes); // 게시물 관련 API
apiRouter.use('/comments', commentRoutes); // 댓글 관련 API
apiRouter.use('/upload', uploadRoutes); // 업로드 관련 API

// 메인 라우터
app.use('/api/v1', apiRouter);

// 에러 핸들러 등록
app.use(errorHandler);

// 서버 실행
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
