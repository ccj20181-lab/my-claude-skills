/**
 * 字幕组件
 * Captions component with word-level highlighting
 */

import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";
import { WordTimestamp } from "../types/scene";

interface CaptionsProps {
  text: string;
  wordTimestamps?: WordTimestamp[] | null;
  startFrame?: number;
  style?: "subtitle" | "overlay";
}

export const Captions: React.FC<CaptionsProps> = ({
  text,
  wordTimestamps,
  startFrame = 0,
  style = "subtitle",
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { colors, typography, spacing, borderRadius } = whiteboardTheme;

  const currentTimeMs = ((frame - startFrame) / fps) * 1000;

  // If we have word timestamps, highlight current word
  const renderWithHighlight = () => {
    if (!wordTimestamps || wordTimestamps.length === 0) {
      return <span>{text}</span>;
    }

    return wordTimestamps.map((word, index) => {
      const isActive =
        currentTimeMs >= word.start_ms && currentTimeMs < word.end_ms;
      const isPast = currentTimeMs >= word.end_ms;

      return (
        <span
          key={index}
          style={{
            color: isActive
              ? colors.accent.blue
              : isPast
              ? colors.text.primary
              : colors.text.muted,
            fontWeight: isActive
              ? typography.fontWeight.bold
              : typography.fontWeight.normal,
            transition: "color 0.1s, font-weight 0.1s",
          }}
        >
          {word.word}
        </span>
      );
    });
  };

  // Fade in animation
  const opacity = interpolate(frame - startFrame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  const styleConfig = {
    subtitle: {
      bottom: 180,
      left: "50%",
      transform: "translateX(-50%)",
      maxWidth: 900,
      padding: `${spacing.sm}px ${spacing.md}px`,
      backgroundColor: "rgba(255, 255, 255, 0.95)",
      borderRadius: borderRadius.md,
      boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
      fontSize: typography.fontSize.md,
    },
    overlay: {
      bottom: 100,
      left: spacing.lg,
      right: spacing.lg,
      padding: `${spacing.md}px`,
      backgroundColor: "rgba(0, 0, 0, 0.7)",
      borderRadius: borderRadius.md,
      fontSize: typography.fontSize.lg,
      color: "white",
    },
  };

  const currentStyle = styleConfig[style];

  return (
    <div
      style={{
        position: "absolute",
        ...currentStyle,
        opacity,
        fontFamily: typography.fontFamily.body,
        textAlign: "center",
        lineHeight: typography.lineHeight.relaxed,
      }}
    >
      {renderWithHighlight()}
    </div>
  );
};
