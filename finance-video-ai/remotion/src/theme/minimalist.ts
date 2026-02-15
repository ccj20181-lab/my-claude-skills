/**
 * 极简主题配置
 * 基于参考视频风格
 */
export const minimalistTheme = {
  colors: {
    background: "#FFFFFF", // 纯白背景
    text: "#000000", // 黑色文字
    accent: "#000000", // 黑色强调
    secondary: "#333333", // 深灰次要
  },
  layout: {
    width: 1080,
    height: 1440, // 3:4 小红书比例
    padding: {
      horizontal: 60,
      vertical: 80,
    },
    logo: {
      width: 60,
      top: 30,
      right: 30,
    },
  },
  typography: {
    fontFamily: "'PingFang SC', 'Noto Sans SC', sans-serif",
    subtitle: {
      fontSize: 36,
      lineHeight: 1.6,
      fontWeight: 500,
    },
  },
  animation: {
    imageEntry: {
      duration: 15, // 帧数
      easing: "spring",
    },
    transition: {
      duration: 12, // 帧数
    },
  },
};

export type Theme = typeof minimalistTheme;
