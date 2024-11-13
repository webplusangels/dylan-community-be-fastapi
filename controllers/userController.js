const userModel = require('../models/userModel');

// 사용자 목록 조회
const getUsers = async (req, res) => {
    try {
        const users = await userModel.getUsers(); // 비동기적으로 사용자 목록 가져오기
        res.json(users); // 성공적으로 가져온 데이터 반환
    } catch (err) {
        res.status(500).json({
            message: '사용자 목록을 가져오는 데 실패했습니다.',
            error: err,
        });
    }
};
module.exports = {
    getUsers,
};
