const express = require('express');
const path = require('path');

const router = express.Router();
const pagesDir = path.join(__dirname, '../../frontend/pages');

router.get('/', (req, res) => {
    res.sendFile(path.join(pagesDir, 'login.html'));
});

module.exports = router;
