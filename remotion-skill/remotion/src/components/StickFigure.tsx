/**
 * 火柴人组件
 * Stick figure character with expressions
 */

import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Img,
  staticFile,
} from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";

interface StickFigureProps {
  type: string;
  imagePath?: string | null;
  position?: "left" | "center" | "right" | "bottom-left" | "bottom-right";
  size?: number;
  animate?: boolean;
}

export const StickFigure: React.FC<StickFigureProps> = ({
  type,
  imagePath,
  position = "bottom-left",
  size = 280,
  animate = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entry animation
  const slideIn = animate
    ? spring({
        frame,
        fps,
        config: {
          damping: 15,
          stiffness: 100,
        },
      })
    : 1;

  // Idle bobbing animation
  const bob = animate
    ? Math.sin(frame / 15) * 5
    : 0;

  // Position styles
  const positionStyles: Record<string, React.CSSProperties> = {
    left: {
      left: 60,
      bottom: 200,
    },
    center: {
      left: "50%",
      bottom: 200,
      transform: `translateX(-50%) translateY(${(1 - slideIn) * 100}px)`,
    },
    right: {
      right: 60,
      bottom: 200,
    },
    "bottom-left": {
      left: 60,
      bottom: 120,
    },
    "bottom-right": {
      right: 60,
      bottom: 120,
    },
  };

  const baseStyle = positionStyles[position] || positionStyles["bottom-left"];

  // If we have an image path, use it
  if (imagePath) {
    return (
      <Img
        src={staticFile(imagePath)}
        style={{
          position: "absolute",
          ...baseStyle,
          width: size,
          height: "auto",
          opacity: slideIn,
          transform: `${baseStyle.transform || ""} translateY(${bob}px)`,
        }}
      />
    );
  }

  // Otherwise render SVG stick figure
  return (
    <div
      style={{
        position: "absolute",
        ...baseStyle,
        width: size,
        height: size * 1.5,
        opacity: slideIn,
        transform: `${baseStyle.transform || ""} translateY(${bob}px)`,
      }}
    >
      <StickFigureSVG type={type} size={size} />
    </div>
  );
};

// SVG Stick Figure based on expression type - 重新设计更可爱的风格
const StickFigureSVG: React.FC<{ type: string; size: number }> = ({
  type,
  size,
}) => {
  // 使用更友好的配色
  const primaryColor = "#2D3748";
  const secondaryColor = "#4A5568";
  const skinColor = "#FEE2B3";
  const cheekColor = "#FFCACA";
  const strokeWidth = 5;

  // 表情映射
  const expressions: Record<string, React.ReactNode> = {
    happy: (
      <>
        {/* 开心的眼睛 - 弯弯的 */}
        <path d="M 32 38 Q 38 32 44 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        <path d="M 56 38 Q 62 32 68 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 开心的嘴巴 */}
        <path d="M 38 52 Q 50 65 62 52" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 腮红 */}
        <ellipse cx="30" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
        <ellipse cx="70" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
      </>
    ),
    thinking: (
      <>
        {/* 思考的眼睛 */}
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        {/* 思考的嘴 - 歪歪的 */}
        <path d="M 42 55 Q 50 52 58 55" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 思考泡泡 */}
        <circle cx="82" cy="15" r="4" fill={secondaryColor} opacity="0.5" />
        <circle cx="88" cy="8" r="6" fill={secondaryColor} opacity="0.5" />
        <circle cx="96" cy="0" r="8" fill={secondaryColor} opacity="0.5" />
      </>
    ),
    confused: (
      <>
        {/* 困惑的眼睛 */}
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        {/* 一边眉毛抬起 */}
        <path d="M 30 30 Q 38 26 46 30" stroke={primaryColor} strokeWidth={2} fill="none" />
        <path d="M 54 32 Q 62 30 70 32" stroke={primaryColor} strokeWidth={2} fill="none" />
        {/* 困惑的嘴 */}
        <path d="M 40 55 Q 45 52 50 55 Q 55 58 60 55" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 问号 */}
        <text x="78" y="25" fontSize="20" fontWeight="bold" fill={primaryColor}>?</text>
      </>
    ),
    surprised: (
      <>
        {/* 惊讶的大眼睛 */}
        <circle cx="38" cy="38" r="6" fill="white" stroke={primaryColor} strokeWidth={2} />
        <circle cx="38" cy="38" r="3" fill={primaryColor} />
        <circle cx="62" cy="38" r="6" fill="white" stroke={primaryColor} strokeWidth={2} />
        <circle cx="62" cy="38" r="3" fill={primaryColor} />
        {/* O形嘴巴 */}
        <ellipse cx="50" cy="55" rx="8" ry="10" fill="white" stroke={primaryColor} strokeWidth={3} />
      </>
    ),
    pointing: (
      <>
        {/* 自信的眼睛 */}
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        {/* 微笑 */}
        <path d="M 42 52 Q 50 58 58 52" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
      </>
    ),
    waving: (
      <>
        {/* 友好的眼睛 */}
        <path d="M 32 38 Q 38 32 44 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        <path d="M 56 38 Q 62 32 68 38" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 开心大嘴 */}
        <path d="M 35 50 Q 50 68 65 50" stroke={primaryColor} strokeWidth={3} fill="none" strokeLinecap="round" />
        {/* 腮红 */}
        <ellipse cx="28" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
        <ellipse cx="72" cy="48" rx="6" ry="4" fill={cheekColor} opacity="0.6" />
      </>
    ),
    neutral: (
      <>
        <circle cx="38" cy="38" r="4" fill={primaryColor} />
        <circle cx="62" cy="38" r="4" fill={primaryColor} />
        <line x1="42" y1="55" x2="58" y2="55" stroke={primaryColor} strokeWidth={3} strokeLinecap="round" />
      </>
    ),
  };

  const expression = expressions[type] || expressions.neutral;

  // 手臂姿势
  const getArms = () => {
    switch (type) {
      case "pointing":
        return (
          <>
            {/* 指向的手臂 */}
            <path d="M 50 90 Q 30 85 15 75" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d="M 50 90 Q 75 75 95 60" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            {/* 指向的手指 */}
            <circle cx="95" cy="60" r="4" fill={skinColor} stroke={primaryColor} strokeWidth={2} />
          </>
        );
      case "waving":
        return (
          <>
            <path d="M 50 90 Q 30 85 15 95" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d="M 50 90 Q 70 70 85 50" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            {/* 挥动的手 */}
            <ellipse cx="88" cy="48" rx="8" ry="10" fill={skinColor} stroke={primaryColor} strokeWidth={2} />
          </>
        );
      default:
        return (
          <>
            <path d="M 50 90 Q 30 95 20 105" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
            <path d="M 50 90 Q 70 95 80 105" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
          </>
        );
    }
  };

  return (
    <svg viewBox="0 0 100 160" width={size} height={size * 1.6}>
      {/* 头部 - 更大更圆润 */}
      <circle cx="50" cy="40" r="30" fill={skinColor} stroke={primaryColor} strokeWidth={strokeWidth} />

      {/* 表情 */}
      {expression}

      {/* 身体 - 圆润的线条 */}
      <path
        d="M 50 70 Q 50 100 50 120"
        stroke={primaryColor}
        strokeWidth={strokeWidth}
        fill="none"
        strokeLinecap="round"
      />

      {/* 手臂 */}
      {getArms()}

      {/* 腿部 - 更自然的姿势 */}
      <path d="M 50 120 Q 40 140 35 155" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
      <path d="M 50 120 Q 60 140 65 155" stroke={primaryColor} strokeWidth={strokeWidth} fill="none" strokeLinecap="round" />
    </svg>
  );
};
