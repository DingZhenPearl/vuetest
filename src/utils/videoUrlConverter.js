/**
 * 视频链接转换工具
 * 将原始视频链接转换为嵌入式外链
 */

/**
 * 将B站视频链接转换为嵌入式外链
 * @param {string} url B站视频链接
 * @returns {string} 嵌入式外链
 */
function convertBilibiliUrl(url) {
  // 提取BV号
  const bvMatch = url.match(/BV\w+/);
  if (!bvMatch) return null;
  
  const bvid = bvMatch[0];
  
  // 提取分P号（如果有）
  let page = 1;
  const pageMatch = url.match(/p=(\d+)/);
  if (pageMatch) {
    page = parseInt(pageMatch[1]);
  }
  
  // 构建嵌入式外链
  return `//player.bilibili.com/player.html?bvid=${bvid}&page=${page}&high_quality=1&danmaku=0&as_wide=1`;
}

/**
 * 将腾讯视频链接转换为嵌入式外链
 * @param {string} url 腾讯视频链接
 * @returns {string} 嵌入式外链
 */
function convertTencentUrl(url) {
  // 提取视频ID
  const vidMatch = url.match(/vid=([^&]+)/);
  if (vidMatch) {
    return `//v.qq.com/txp/iframe/player.html?vid=${vidMatch[1]}`;
  }
  
  // 另一种URL格式
  const pathMatch = url.match(/\/([a-zA-Z0-9]+)\.html/);
  if (pathMatch) {
    return `//v.qq.com/txp/iframe/player.html?vid=${pathMatch[1]}`;
  }
  
  return null;
}

/**
 * 将优酷视频链接转换为嵌入式外链
 * @param {string} url 优酷视频链接
 * @returns {string} 嵌入式外链
 */
function convertYoukuUrl(url) {
  // 提取视频ID
  const idMatch = url.match(/id_([a-zA-Z0-9=]+)/);
  if (idMatch) {
    return `//player.youku.com/embed/${idMatch[1]}`;
  }
  
  return null;
}

/**
 * 将爱奇艺视频链接转换为嵌入式外链
 * @param {string} url 爱奇艺视频链接
 * @returns {string} 嵌入式外链
 */
function convertIqiyiUrl(url) {
  // 提取视频ID
  const idMatch = url.match(/([a-zA-Z0-9]+)\.html/);
  if (idMatch) {
    return `//www.iqiyi.com/common/flashplayer/20230628/PlayerJS_1.js?vid=${idMatch[1]}`;
  }
  
  return null;
}

/**
 * 将YouTube视频链接转换为嵌入式外链
 * @param {string} url YouTube视频链接
 * @returns {string} 嵌入式外链
 */
function convertYoutubeUrl(url) {
  // 提取视频ID
  const idMatch = url.match(/(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  if (idMatch) {
    return `//www.youtube.com/embed/${idMatch[1]}`;
  }
  
  return null;
}

/**
 * 检测视频链接类型
 * @param {string} url 视频链接
 * @returns {string} 视频平台类型
 */
function detectVideoType(url) {
  if (!url) return 'unknown';
  
  if (url.includes('bilibili.com')) return 'bilibili';
  if (url.includes('v.qq.com')) return 'tencent';
  if (url.includes('youku.com')) return 'youku';
  if (url.includes('iqiyi.com')) return 'iqiyi';
  if (url.includes('youtube.com') || url.includes('youtu.be')) return 'youtube';
  
  // 检查是否已经是嵌入式链接
  if (url.includes('player.bilibili.com')) return 'bilibili-embed';
  if (url.includes('v.qq.com/txp/iframe')) return 'tencent-embed';
  if (url.includes('player.youku.com')) return 'youku-embed';
  if (url.includes('iqiyi.com/common/flashplayer')) return 'iqiyi-embed';
  if (url.includes('youtube.com/embed')) return 'youtube-embed';
  
  return 'unknown';
}

/**
 * 将原始视频链接转换为嵌入式外链
 * @param {string} url 原始视频链接
 * @returns {object} 转换结果，包含转换后的URL和视频平台类型
 */
export function convertVideoUrl(url) {
  if (!url) return { embedUrl: '', type: 'unknown' };
  
  // 检测视频类型
  const type = detectVideoType(url);
  
  // 如果已经是嵌入式链接，直接返回
  if (type.endsWith('-embed')) {
    return { 
      embedUrl: url, 
      type: type.replace('-embed', ''),
      isConverted: false
    };
  }
  
  // 根据类型转换链接
  let embedUrl = '';
  switch (type) {
    case 'bilibili':
      embedUrl = convertBilibiliUrl(url);
      break;
    case 'tencent':
      embedUrl = convertTencentUrl(url);
      break;
    case 'youku':
      embedUrl = convertYoukuUrl(url);
      break;
    case 'iqiyi':
      embedUrl = convertIqiyiUrl(url);
      break;
    case 'youtube':
      embedUrl = convertYoutubeUrl(url);
      break;
    default:
      embedUrl = url; // 未知类型，保持原样
  }
  
  return { 
    embedUrl: embedUrl || url, 
    type,
    isConverted: !!embedUrl && embedUrl !== url
  };
}

export default {
  convertVideoUrl
};
