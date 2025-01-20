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

// 날짜 포맷 함수 (한국 시간)
const formatDate = (date) => {
    const options = {
        timeZone: 'Asia/Seoul',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false, // 24시간 형식 사용
    };

    // 한국 시간대로 변환된 문자열을 얻음
    const koreanDateStr = date.toLocaleString('en-US', options);

    // 문자열을 원하는 포맷으로 변환
    const [datePart, timePart] = koreanDateStr.split(', ');
    const [month, day, year] = datePart.split('/');
    const [hour, minute, second] = timePart.split(':');

    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hour.padStart(2, '0')}:${minute.padStart(2, '0')}:${second.padStart(2, '0')}`;
};

// 세션 사용자 설정 함수
const setSessionUser = (req, user) => {
    req.session.user = {
        user_id: user.user_id,
        email: user.email,
        nickname: user.nickname,
        profile_image_path: user.profile_image_path,
        viewed: user.viewed,
    };
};

module.exports = {
    getById,
    createRecord,
    formatDate,
    setSessionUser,
};
