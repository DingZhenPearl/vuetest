/**
 * 导入章节数据到后端数据库
 * 
 * 使用方法：
 * 1. 确保服务器已启动
 * 2. 在终端中运行: node src/scripts/import-chapters.js
 */

const chaptersData = require('../data/chapters-data');

// 教师邮箱，可以根据需要修改
const teacherEmail = 'teacher@example.com';

/**
 * 导入章节数据
 */
async function importChapters() {
  console.log('开始导入章节数据...');
  
  try {
    // 遍历所有章节
    for (const chapter of chaptersData) {
      // 准备章节数据
      const chapterData = {
        teacher_email: teacherEmail,
        chapter_id: chapter.id,
        chapter_number: chapter.number,
        chapter_title: chapter.title,
        chapter_difficulty: chapter.difficulty,
        chapter_description: chapter.description,
        sections: chapter.sections
      };
      
      console.log(`正在导入章节: ${chapter.title}`);
      
      // 发送请求添加章节
      const response = await fetch('http://localhost:3000/api/teaching-content/chapters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(chapterData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log(`章节 "${chapter.title}" 导入成功`);
      } else {
        console.error(`章节 "${chapter.title}" 导入失败: ${result.message}`);
      }
    }
    
    console.log('章节数据导入完成');
  } catch (error) {
    console.error('导入章节数据时出错:', error);
  }
}

// 执行导入
importChapters();
