/**
 * 字幕组件
 * 支持词级别高亮
 */
import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  spring,
} from "remotion";
import { WordTimestamp } from "../types/scene";
import { minimalistTheme } from "../theme/minimalist";

interface SubtitleProps {
  text: string;
  durationInFrames: number;
  wordTimestamps?: WordTimestamp[] | null;
  accentColor?: string;
  style?: "compact" | "centered";
}

export const Subtitle: React.FC<SubtitleProps> = ({
  text,
  durationInFrames,
  wordTimestamps,
  accentColor = minimalistTheme.colors.accent,
  style = "compact",
}) => {
  const frame = useCurrentFrame();
  const fps = 30;

  // 入场动画
  const entryProgress = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 100 },
  });

  // 当前时间（毫秒）
  const currentTimeMs = (frame / fps) * 1000;

  // 渲染文本
  const renderText = () => {
    if (!wordTimestamps || wordTimestamps.length === 0) {
      // 无时间戳时，显示纯文本
      return (
        <span
          style={{
            fontFamily: minimalistTheme.typography.fontFamily,
            fontSize: minimalistTheme.typography.subtitle.fontSize,
            fontWeight: minimalistTheme.typography.subtitle.fontWeight,
            color: minimalistTheme.colors.text,
          }}
        >
          {text}
        </span>
      );
    }

    // 有时间戳时，高亮当前词
    return (
      <span
        style={{
          fontFamily: minimalistTheme.typography.fontFamily,
          fontSize: minimalistTheme.typography.subtitle.fontSize,
          fontWeight: minimalistTheme.typography.subtitle.fontWeight,
          color: minimalistTheme.colors.text,
          lineHeight: minimalistTheme.typography.subtitle.lineHeight,
        }}
      >
        {wordTimestamps.map((wt, index) => {
          const isActive =
            currentTimeMs >= wt.start_ms && currentTimeMs <= wt.end_ms;
          const isPast = currentTimeMs > wt.end_ms;

          return (
            <span
              key={index}
              style={{
                color: isPast
                  ? minimalistTheme.colors.secondary
                  : isActive
                  ? accentColor
                  : minimalistTheme.colors.text,
                transition: "color 0.1s ease",
              }}
            >
              {wt.word}
            </span>
          );
        })}
      </span>
    );
  };

  const containerStyle: React.CSSProperties =
    style === "compact"
      ? {
          position: "absolute",
          bottom: 80,
          left: 60,
          right: 60,
          textAlign: "center",
          transform: `translateY(${(1 - entryProgress) * 20}px)`,
          opacity: entryProgress,
        }
      : {
          position: "absolute",
          bottom: 120,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 60px",
          transform: `translateY(${(1 - entryProgress) * 20}px)`,
          opacity: entryProgress,
        };

  // 背景遮罩样式
  const backgroundStyle: React.CSSProperties = {
    position: "absolute",
    bottom: 60,
    left: 40,
    right: 40,
    padding: "16px 24px",
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0, 0, 0, 0.1)",
  };

  return (
    <div style={backgroundStyle}>
      <div style={containerStyle}>{renderText()}</div>
    </div>
  );
};
