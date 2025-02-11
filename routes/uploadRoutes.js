const express = require('express');
const AWS = require('aws-sdk');
const { v4: uuidv4 } = require('uuid');

const router = express.Router();

const s3 = new AWS.S3({
    region: process.env.AWS_REGION,
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
});

// ✅ **Presigned URL 생성 API**
router.get('/generate-presigned-url', async (req, res) => {
    const { fileName, fileType, category } = req.query;

    if (!fileName || !fileType || !category) {
        res.status(400).json({
            error: '파일 이름, 파일 타입, 카테고리가 모두 필요합니다',
        });
        return;
    }
    const folder = category === 'profile' ? 'profiles' : 'posts';
    const extension = fileName.split('.').pop(); // 확장자 추출
    const newFileName = `${folder}/${uuidv4()}.${extension}`;
    const s3Params = {
        Bucket: process.env.S3_BUCKET_NAME,
        Key: `images/${newFileName}`,
        Expires: 60, // Presigned URL 유효 시간 (초)
        ContentType: fileType,
        ACL: `private`,
    };

    try {
        const uploadURL = await s3.getSignedUrlPromise('putObject', s3Params);

        res.json({ uploadURL, newFileName });
    } catch (error) {
        console.error('Presigned URL 생성 중 에러:', error);
        res.status(500).json({
            error: 'Presigned URL을 만드는데 실패했습니다',
        });
    }
});

module.exports = router;
