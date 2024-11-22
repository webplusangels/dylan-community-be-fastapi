const { ERROR_MESSAGES } = require('../config/constants');

// 에러 처리 미들웨어
const errorHandler = (err, req, res, next) => {
    console.error('에러 발생:', err.message);

    if (process.env.NODE_ENV === 'development') {
        console.error(err.stack);
    }

    if (res.headersSent) {
        next(err);
        return;
    }

    res.status(err.status || 500).json({
        message: err.message || ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack }), // 개발 환경에서는 스택 트레이스도 응답에 포함
    });
};

module.exports = errorHandler;
