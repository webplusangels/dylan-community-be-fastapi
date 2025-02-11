const AWS = require('aws-sdk');

const s3 = new AWS.S3({
    region: process.env.AWS_REGION,
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
});

const deleteProfileImage = async (userId, fileName) => {
    if (!fileName) return;

    const s3Params = {
        Bucket: process.env.S3_BUCKET_NAME,
        Key: `profiles/${fileName}`,
    };

    try {
        await s3.deleteObject(s3Params).promise();
        console.log(`✅ 프로필 이미지 삭제 완료: ${fileName}`);
    } catch (error) {
        console.error('❌ 프로필 이미지 삭제 실패:', error);
    }
};

module.exports = {
    deleteProfileImage,
};
