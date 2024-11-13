const mysql = require('mysql2');
require('dotenv').config();

// 환경 변수가 설정되었는지 확인
if (
    !process.env.DB_HOST ||
    !process.env.DB_USER ||
    !process.env.DB_PASSWORD ||
    !process.env.DB_DATABASE
) {
    console.error(
        'Database configuration is missing. Please check your .env file.'
    );
    process.exit(1);
}

const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE,
});

db.connect((err) => {
    if (err) {
        console.error('DB connection error:', err.stack);
        process.exit(1); // 에러
    }
    console.log('Connected to db.');
});

module.exports = db;
