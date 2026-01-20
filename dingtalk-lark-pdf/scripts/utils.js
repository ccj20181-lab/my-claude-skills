#!/usr/bin/env node

/**
 * 工具函数模块
 */

const fs = require('fs');
const path = require('path');

/**
 * 清理文件名，移除非法字符
 * @param {string} filename - 原始文件名
 * @returns {string} 清理后的文件名
 */
function sanitizeFilename(filename) {
  // 移除或替换非法字符
  return filename
    .replace(/[<>:"/\\|?*]/g, '_') // Windows 非法字符
    .replace(/[\x00-\x1f\x80-\x9f]/g, '_') // 控制字符
    .replace(/^\.+/, '') // 开头的点
    .replace(/\s+/g, '_') // 空格替换为下划线
    .substring(0, 200); // 限制长度
}

/**
 * 生成时间戳字符串
 * @returns {string} 时间戳
 */
function getTimestamp() {
  const now = new Date();
  return now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
}

/**
 * 确保目录存在
 * @param {string} dirPath - 目录路径
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * 删除临时文件
 * @param {Array<string>} files - 文件路径列表
 */
function cleanupTempFiles(files) {
  files.forEach((file) => {
    try {
      if (fs.existsSync(file)) {
        fs.unlinkSync(file);
      }
    } catch (err) {
      console.warn(`Failed to delete temp file ${file}:`, err.message);
    }
  });
}

/**
 * 从 URL 提取文档标题
 * @param {string} url - 文档 URL
 * @returns {string} 文档标题
 */
function extractTitleFromUrl(url) {
  try {
    const urlObj = new URL(url);
    const pathname = urlObj.pathname;

    // 尝试从路径提取
    const segments = pathname.split('/').filter(Boolean);
    if (segments.length > 0) {
      const lastSegment = segments[segments.length - 1];
      if (lastSegment && lastSegment.length > 0) {
        return sanitizeFilename(lastSegment);
      }
    }

    // 使用域名作为备用
    return `document_${getTimestamp()}`;
  } catch (err) {
    return `document_${getTimestamp()}`;
  }
}

/**
 * 生成输出文件名
 * @param {string} title - 文档标题
 * @param {string} outputDir - 输出目录
 * @returns {string} 完整的 PDF 文件路径
 */
function generateOutputPath(title, outputDir) {
  const sanitizedTitle = sanitizeFilename(title);
  const filename = `${sanitizedTitle}.pdf`;
  return path.join(outputDir, filename);
}

/**
 * 延迟执行
 * @param {number} ms - 毫秒数
 * @returns {Promise}
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的大小
 */
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

module.exports = {
  sanitizeFilename,
  getTimestamp,
  ensureDir,
  cleanupTempFiles,
  extractTitleFromUrl,
  generateOutputPath,
  sleep,
  formatFileSize,
};
