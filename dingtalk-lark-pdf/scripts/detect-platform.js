#!/usr/bin/env node

/**
 * 平台检测模块
 * 根据 URL 自动识别是钉钉还是飞书文档
 */

/**
 * 检测文档平台类型
 * @param {string} url - 文档 URL
 * @returns {string} 平台类型: 'dingtalk' | 'lark' | 'unknown'
 */
function detectPlatform(url) {
  if (!url) {
    return 'unknown';
  }

  const lowerUrl = url.toLowerCase();

  // 钉钉文档域名
  if (
    lowerUrl.includes('dingtalk.com') ||
    lowerUrl.includes('alidocs.dingtalk.com') ||
    lowerUrl.includes('dingtalk')
  ) {
    return 'dingtalk';
  }

  // 飞书文档域名
  if (
    lowerUrl.includes('feishu.cn') ||
    lowerUrl.includes('docs.feishu.cn') ||
    lowerUrl.includes('feishu')
  ) {
    return 'lark';
  }

  return 'unknown';
}

/**
 * 验证 URL 是否为支持的格式
 * @param {string} url - 文档 URL
 * @returns {boolean} 是否支持
 */
function isValidUrl(url) {
  const platform = detectPlatform(url);
  return platform !== 'unknown';
}

/**
 * 获取平台配置
 * @param {string} platform - 平台类型
 * @returns {object} 平台配置
 */
function getPlatformConfig(platform) {
  const configs = {
    dingtalk: {
      name: '钉钉文档',
      defaultScreenshots: 21,
      defaultScrollWait: 3000,
      defaultInitialWait: 15000,
      hasIframe: true,
      viewportWidth: 1920,
      viewportHeight: 1080,
    },
    lark: {
      name: '飞书文档',
      defaultScreenshots: 30,
      defaultScrollWait: 3000,
      defaultInitialWait: 15000,
      hasIframe: false,
      viewportWidth: 1920,
      viewportHeight: 720,
    },
  };

  return configs[platform] || null;
}

module.exports = {
  detectPlatform,
  isValidUrl,
  getPlatformConfig,
};
