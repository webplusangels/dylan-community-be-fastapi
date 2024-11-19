const { query } = require('./dbUtils');

// ID로 단일 레코드 조회 함수
const getById = async (table, id) => {
    try {
        const sql = `
            SELECT *
            FROM ${table}
            WHERE id = ?`;
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

module.exports = {
    getById,
    createRecord,
    formatDate,
};
