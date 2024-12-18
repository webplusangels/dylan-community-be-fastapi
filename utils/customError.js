/* eslint-disable max-classes-per-file */
class CustomError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.status = status; // HTTP 상태 코드
        this.data = data; // 추가 데이터
        Error.captureStackTrace(this, this.constructor); // 스택 트레이스 유지
    }
}

// 4xx 에러 클래스
class BadRequestError extends CustomError {
    constructor(message = 'Bad Request', data = null) {
        super(message, 400, data);
    }
}

class UnauthorizedError extends CustomError {
    constructor(message = 'Unauthorized') {
        super(message, 401);
        Error.captureStackTrace(this, this.constructor);
    }
}

class ForbiddenError extends CustomError {
    constructor(message = 'Forbidden') {
        super(message, 403);
    }
}

class NotFoundError extends CustomError {
    constructor(message = 'Not Found') {
        super(message, 404);
    }
}

// 5xx 에러 클래스
class InternalServerError extends CustomError {
    constructor(message = 'Internal Server Error') {
        super(message, 500);
    }
}

class ServiceUnavailableError extends CustomError {
    constructor(message = 'Service Unavailable') {
        super(message, 503);
    }
}

module.exports = {
    CustomError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    InternalServerError,
    ServiceUnavailableError,
};
