/**
 * 白板主题配置
 * Whiteboard theme configuration for Miaodong Finance videos
 */

export const whiteboardTheme = {
  // Colors
  colors: {
    background: "#FCFCFA",
    surface: "#FFFFFF",
    text: {
      primary: "#1A202C",
      secondary: "#4A5568",
      muted: "#718096",
    },
    accent: {
      blue: "#3182CE",
      green: "#38A169",
      red: "#E53E3E",
      orange: "#DD6B20",
      purple: "#805AD5",
      pink: "#D53F8C",
    },
    border: "#E2E8F0",
    shadow: "rgba(0, 0, 0, 0.1)",
  },

  // Typography
  typography: {
    fontFamily: {
      heading: '"PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif',
      body: '"PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif',
      mono: '"SF Mono", "Fira Code", monospace',
    },
    fontSize: {
      xs: 20,
      sm: 24,
      md: 32,
      lg: 40,
      xl: 48,
      "2xl": 56,
      "3xl": 72,
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
    },
  },

  // Spacing
  spacing: {
    xs: 8,
    sm: 16,
    md: 24,
    lg: 40,
    xl: 64,
    "2xl": 96,
  },

  // Border radius
  borderRadius: {
    sm: 8,
    md: 16,
    lg: 24,
    full: 9999,
  },

  // Shadows
  shadows: {
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
    xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
  },

  // Animation durations (in frames at 30fps)
  animation: {
    fast: 8, // ~0.27s
    normal: 15, // 0.5s
    slow: 30, // 1s
    verySlow: 60, // 2s
  },

  // Layout
  layout: {
    width: 1080,
    height: 1440,
    padding: {
      horizontal: 60,
      vertical: 80,
    },
    logo: {
      width: 120,
      top: 40,
      right: 40,
    },
    watermark: {
      bottom: 40,
      right: 40,
      fontSize: 28,
    },
  },
};

export type Theme = typeof whiteboardTheme;
