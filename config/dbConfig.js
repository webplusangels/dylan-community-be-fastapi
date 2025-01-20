const mysql = require('mysql2/promise');
const dotenv = require('dotenv');

dotenv.config();

// 환경 변수가 설정되었는지 확인
if (
    !process.env.DB_HOST ||
    !process.env.DB_USER ||
    !process.env.DB_PASSWORD ||
    !process.env.DB_DATABASE
) {
    console.error('데이터베이스 환경변수 설정 실패');
    process.exit(1);
}

const pool = mysql.createPool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
});

pool.getConnection()
    .then((conn) => {
        console.log('데이터베이스에 연결되었습니다.');
        conn.release();
    })
    .catch((err) => {
        console.error('데이터베이스 연결 에러:', err.message);
    });

module.exports = pool;
