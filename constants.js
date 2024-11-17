module.exports = {
    ERROR_MESSAGES: {
        FETCH_USERS: '사용자 목록을 가져오는 데 실패했습니다.',
        REGISTER_USER: '사용자를 등록하는 데 실패했습니다.',
        LOGIN_USER: '사용자를 로그인하는 데 실패했습니다.',
        INVALID_CREDENTIALS: '잘못된 자격 증명입니다.',
        USER_NOT_FOUND: '사용자를 찾을 수 없습니다.',
        UPDATE_USER: '사용자 정보를 업데이트하는 데 실패했습니다.',
        DELETE_USER: '사용자를 삭제하는 데 실패했습니다.',
        INTERNAL_SERVER_ERROR: '서버 내부 오류',
    },
    ROLES: {
        ADMIN: 'admin',
        USER: 'user',
        GUEST: 'guest',
    },
    DEFAULTS: {
        USER_PROFILE_IMAGE: '/images/default-profile.png',
        SESSION_TIMEOUT: 1000 * 60 * 60 * 24, // 1일
    },
    PATHS: {
        USER_DATA: '/data/users.json',
        LOGS: '/logs/app.log',
    },
};
