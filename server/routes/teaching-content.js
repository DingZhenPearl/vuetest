/**
 * 教学内容管理相关路由
 */
const express = require('express');
const router = express.Router();
const { executePythonScript } = require('../services/python');

/**
 * 创建必要的数据表
 */
router.post('/init', async (req, res) => {
    try {
        const result = await executePythonScript('teaching_content.py', ['create_tables']);
        res.json(result);
    } catch (error) {
        console.error('初始化教学内容表失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 获取所有章节
 */
router.get('/chapters', async (req, res) => {
    try {
        const result = await executePythonScript('teaching_content.py', ['get_all_chapters']);
        res.json(result);
    } catch (error) {
        console.error('获取章节列表失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 获取指定章节
 */
router.get('/chapters/:chapterId', async (req, res) => {
    try {
        const { chapterId } = req.params;
        const result = await executePythonScript('teaching_content.py', ['get_chapter', chapterId]);
        res.json(result);
    } catch (error) {
        console.error('获取章节失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 添加新章节
 */
router.post('/chapters', async (req, res) => {
    try {
        const chapterData = req.body;
        
        // 验证必要字段
        const requiredFields = [
            'teacher_email', 'chapter_id', 'chapter_number', 'chapter_title',
            'chapter_difficulty', 'chapter_description', 'sections'
        ];
        
        for (const field of requiredFields) {
            if (!chapterData[field]) {
                return res.status(400).json({
                    success: false,
                    message: `缺少必要字段: ${field}`
                });
            }
        }
        
        const result = await executePythonScript('teaching_content.py', [
            'add_chapter',
            JSON.stringify(chapterData)
        ]);
        
        res.json(result);
    } catch (error) {
        console.error('添加章节失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 更新章节
 */
router.put('/chapters/:chapterId', async (req, res) => {
    try {
        const { chapterId } = req.params;
        const chapterData = req.body;
        
        // 确保章节ID一致
        if (chapterData.chapter_id !== chapterId) {
            return res.status(400).json({
                success: false,
                message: '章节ID不匹配'
            });
        }
        
        // 验证必要字段
        const requiredFields = [
            'chapter_id', 'chapter_number', 'chapter_title',
            'chapter_difficulty', 'chapter_description', 'sections'
        ];
        
        for (const field of requiredFields) {
            if (!chapterData[field]) {
                return res.status(400).json({
                    success: false,
                    message: `缺少必要字段: ${field}`
                });
            }
        }
        
        const result = await executePythonScript('teaching_content.py', [
            'update_chapter',
            JSON.stringify(chapterData)
        ]);
        
        res.json(result);
    } catch (error) {
        console.error('更新章节失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

/**
 * 删除章节
 */
router.delete('/chapters/:chapterId', async (req, res) => {
    try {
        const { chapterId } = req.params;
        const result = await executePythonScript('teaching_content.py', ['delete_chapter', chapterId]);
        res.json(result);
    } catch (error) {
        console.error('删除章节失败:', error);
        res.status(500).json({
            success: false,
            message: '服务器错误',
            error: error.message
        });
    }
});

module.exports = router;
