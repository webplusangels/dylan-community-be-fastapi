const { query } = require('./dbUtils');

// ID로 단일 레코드 조회 함수
const getById = async (table, id, idField = 'id') => {
    if (!table || typeof table !== 'string') {
        throw new Error('유효한 테이블 이름이 필요합니다.');
    }
    if (!id) {
        throw new Error('유효한 ID가 필요합니다.');
    }

    try {
        const sql = `
            SELECT *
            FROM ${table}
            WHERE ${idField} = ?`;
        const rows = await query(sql, [id]);
        if (!rows.length) {
            throw new Error(`${table}를 찾을 수 없습니다.`);
        }
        return rows[0];
    } catch (error) {
        console.error(`${table} 데이터 조회 오류:`, error.message);
        throw error;
    }
};

// 레코드 생성 함수
const createRecord = async (table, data) => {
    if (!table || typeof table !== 'string') {
        throw new Error('유효한 테이블 이름이 필요합니다.');
    }
    if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
        throw new Error('유효한 데이터가 필요합니다.');
    }

    try {
        const columns = Object.keys(data).join(', ');
        const placeholders = Object.keys(data)
            .map(() => '?')
            .join(', ');
        const sql = `
            INSERT INTO ${table} (${columns})
            VALUES (${placeholders})
        `;
        const result = await query(sql, Object.values(data));
        return result.insertId;
    } catch (error) {
        console.error(`${table} 생성 오류:`, error.message);
        throw error;
    }
};

// 날짜 포맷 함수
const formatDate = (date) => {
    return date.toISOString().slice(0, 19).replace('T', ' ');
};

// 세션 사용자 설정 함수
const setSessionUser = (req, user) => {
    req.session.user = {
        user_id: user.user_id,
        email: user.email,
        nickname: user.nickname,
        profile_image_path: user.profile_image_path,
    };
};

module.exports = {
    getById,
    createRecord,
    formatDate,
    setSessionUser,
};
