const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { authenticateToken } = require('./utils/jwt');
const errorHandler = require('./middlewares/errorHandler');
const authRouter = require('./routes/authRoutes');
const userRoutes = require('./routes/userRoutes');
const postRoutes = require('./routes/postRoutes');
const commentRoutes = require('./routes/commentRoutes');
const uploadRoutes = require('./routes/uploadRoutes');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 8000;
if (!process.env.DB_HOST || !process.env.DB_USER || !process.env.JWT_SECRET) {
    console.error('환경 변수 설정이 올바르지 않습니다. 서버를 종료합니다.');
    process.exit(1);
}

// 미들웨어 설정
app.use(express.json());
app.use(
    cors({
        origin: [
            'http://localhost:3000',
            'http://dylan-web-app-bucket.s3-website.ap-northeast-2.amazonaws.com',
        ],
        credentials: true,
        methods: 'GET,POST,PUT,DELETE,OPTIONS',
        allowedHeaders:
            'Origin,X-Requested-With,Content-Type,Accept,Authorization,Set-Cookie',
        exposedHeaders: ['Set-Cookie'],
    })
);
app.use(
    '/api/',
    rateLimit({
        windowMs: 60 * 1000,
        max: 100,
        message: '잠시 후에 다시 시도하세요',
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

apiRouter.get('/test', (req, res) => {
    res.status(200).json({ message: 'Server is running' });
});

// 보호된 라우트 예시
apiRouter.get('/protected', authenticateToken, (req, res) => {
    res.json({ message: 'This is a protected route', user: req.user });
});

app.use((req, res, next) => {
    console.log(`📌 요청됨: ${req.method} ${req.originalUrl}`);
    next();
});

// 메인 라우터
app.use('/api/v1', apiRouter);

// 에러 핸들러 등록
app.use(errorHandler);

// 서버 실행
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
