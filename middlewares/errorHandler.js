const { ERROR_MESSAGES } = require('../config/constants');
const { CustomError } = require('../utils/customError');

// 에러 처리 미들웨어
const errorHandler = (err, req, res, next) => {
    console.error('에러 발생:', err.message);

    if (process.env.NODE_ENV === 'development') {
        console.error(err.stack);
    }

    if (res.headersSent) {
        return next(err);
    }

    if (err instanceof CustomError) {
        return res.status(err.status).json({
            message: err.message,
            data: err.data,
        });
    }

    if (err.status === 401) {
        return res.status(401).json({
            message: '로그인이 필요합니다.',
        });
    }

    if (err.status === 403) {
        return res.status(403).json({
            success: false,
            message: '접근이 금지되었습니다.',
        });
    }

    if (err.status === 404) {
        return res.status(404).json({
            success: false,
            message: '리소스를 찾을 수 없습니다.',
        });
    }

    return res.status(err.status || 500).json({
        message: err.message || ERROR_MESSAGES.INTERNAL_SERVER_ERROR,
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack }), // 개발 환경에서는 스택 트레이스도 응답에 포함
    });
};

module.exports = errorHandler;
