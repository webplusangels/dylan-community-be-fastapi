const getUploadedFileUrl = (file) => {
    if (!file) {
        throw new Error('이미지 업로드 실패');
    }

    return `${file.filename}`;
};

module.exports = {
    getUploadedFileUrl,
};
