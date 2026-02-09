/**
 * 手绘动画效果组件
 * Hand-drawn animation effects
 */

import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

interface HandDrawProps {
  type: "underline" | "circle" | "arrow" | "checkmark" | "cross";
  color?: string;
  strokeWidth?: number;
  delay?: number;
  duration?: number;
}

export const HandDraw: React.FC<HandDrawProps> = ({
  type,
  color = "#3182CE",
  strokeWidth = 4,
  delay = 0,
  duration = 20,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);
  const progress = interpolate(adjustedFrame, [0, duration], [0, 1], {
    extrapolateRight: "clamp",
  });

  const renderPath = () => {
    switch (type) {
      case "underline":
        return (
          <svg width="200" height="20" viewBox="0 0 200 20">
            <path
              d="M 5 15 Q 50 10 100 15 Q 150 20 195 12"
              stroke={color}
              strokeWidth={strokeWidth}
              fill="none"
              strokeLinecap="round"
              strokeDasharray={200}
              strokeDashoffset={200 * (1 - progress)}
            />
          </svg>
        );

      case "circle":
        return (
          <svg width="120" height="120" viewBox="0 0 120 120">
            <ellipse
              cx="60"
              cy="60"
              rx="50"
              ry="45"
              stroke={color}
              strokeWidth={strokeWidth}
              fill="none"
              strokeLinecap="round"
              strokeDasharray={320}
              strokeDashoffset={320 * (1 - progress)}
              transform="rotate(-10 60 60)"
            />
          </svg>
        );

      case "arrow":
        return (
          <svg width="100" height="60" viewBox="0 0 100 60">
            <path
              d="M 10 30 L 70 30 M 55 15 L 70 30 L 55 45"
              stroke={color}
              strokeWidth={strokeWidth}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={120}
              strokeDashoffset={120 * (1 - progress)}
            />
          </svg>
        );

      case "checkmark":
        return (
          <svg width="60" height="60" viewBox="0 0 60 60">
            <path
              d="M 10 35 L 25 50 L 50 15"
              stroke={color}
              strokeWidth={strokeWidth}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray={80}
              strokeDashoffset={80 * (1 - progress)}
            />
          </svg>
        );

      case "cross":
        return (
          <svg width="50" height="50" viewBox="0 0 50 50">
            <path
              d="M 10 10 L 40 40 M 40 10 L 10 40"
              stroke={color}
              strokeWidth={strokeWidth}
              fill="none"
              strokeLinecap="round"
              strokeDasharray={85}
              strokeDashoffset={85 * (1 - progress)}
            />
          </svg>
        );

      default:
        return null;
    }
  };

  return <div style={{ display: "inline-block" }}>{renderPath()}</div>;
};

// Animated highlight box
export const HighlightBox: React.FC<{
  children: React.ReactNode;
  color?: string;
  delay?: number;
}> = ({ children, color = "#FEF3C7", delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const adjustedFrame = Math.max(0, frame - delay);
  const width = spring({
    frame: adjustedFrame,
    fps,
    config: { damping: 20, stiffness: 100 },
  });

  return (
    <span style={{ position: "relative", display: "inline-block" }}>
      <span
        style={{
          position: "absolute",
          left: 0,
          bottom: 0,
          height: "40%",
          width: `${width * 100}%`,
          backgroundColor: color,
          zIndex: -1,
        }}
      />
      {children}
    </span>
  );
};

// Wobble animation for emphasis
export const Wobble: React.FC<{
  children: React.ReactNode;
  intensity?: number;
  speed?: number;
}> = ({ children, intensity = 3, speed = 10 }) => {
  const frame = useCurrentFrame();

  const rotation = Math.sin(frame / speed) * intensity;

  return (
    <div
      style={{
        display: "inline-block",
        transform: `rotate(${rotation}deg)`,
      }}
    >
      {children}
    </div>
  );
};
