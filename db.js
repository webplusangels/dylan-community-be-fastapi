const pool = require('./config/dbConfig');

// SELECT 쿼리 실행
async function query(sql, params) {
    const connection = await pool.getConnection();
    try {
        const [rows] = await connection.query(sql, params);
        return rows;
    } catch (error) {
        console.error('Query Error:', error);
        throw error;
    } finally {
        connection.release();
    }
}

// INSERT, UPDATE, DELETE 쿼리 실행
async function execute(sql, params) {
    const connection = await pool.getConnection();
    try {
        const [result] = await connection.execute(sql, params);
        return result;
    } catch (error) {
        console.error('Execution Error:', error);
        throw error;
    } finally {
        connection.release();
    }
}

module.exports = { query, execute };
