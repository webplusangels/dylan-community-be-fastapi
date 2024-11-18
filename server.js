const express = require('express');
const dotenv = require('dotenv');
const session = require('express-session');
const { DEFAULTS } = require('./constants');

// const pagesRouter = require('./routes/pages');
const userRoutes = require('./routes/userRoutes');
const postRoutes = require('./routes/postRoutes');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어 설정
app.use(express.json());
app.use(
    /* 세션 설정 */
    session({
        secret: process.env.COOKIE_SECRET,
        resave: false,
        saveUninitialized: true,
        cookie: {
            httpOnly: true,
            secure: false,
            maxAge: DEFAULTS.SESSION_TIMEOUT,
        },
    })
);

// 라우터 등록
// 서브 라우터
const apiRouter = express.Router();
apiRouter.use('/users', userRoutes); // 사용자 관련 API
apiRouter.use('/posts', postRoutes); // 게시물 관련 API
// app.use('/', express.static('frontend/pages')); // 프론트엔드 페이지

// 메인 라우터
app.use('/api/v1', apiRouter);

// 서버 실행
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
