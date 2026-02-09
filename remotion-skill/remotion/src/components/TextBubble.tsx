/**
 * 文字气泡组件
 * Text bubble with hand-drawn style
 */

import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";
import { SceneType, SCENE_STYLES } from "../types/scene";

interface TextBubbleProps {
  text: string;
  sceneType?: SceneType;
  position?: "top" | "center" | "bottom";
  maxWidth?: number;
  animate?: boolean;
}

export const TextBubble: React.FC<TextBubbleProps> = ({
  text,
  sceneType = "explain",
  position = "center",
  maxWidth = 900,
  animate = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { colors, typography, spacing, borderRadius } = whiteboardTheme;

  const sceneStyle = SCENE_STYLES[sceneType];

  // Animation: fade in and scale up
  const opacity = animate
    ? interpolate(frame, [0, 15], [0, 1], {
        extrapolateRight: "clamp",
      })
    : 1;

  const scale = animate
    ? spring({
        frame,
        fps,
        config: {
          damping: 15,
          stiffness: 120,
        },
      })
    : 1;

  // Text reveal animation (character by character)
  const visibleChars = animate
    ? Math.floor(interpolate(frame, [10, 10 + text.length * 2], [0, text.length], {
        extrapolateRight: "clamp",
      }))
    : text.length;

  const displayText = text.slice(0, visibleChars);

  // Position styles
  const positionStyles: Record<string, React.CSSProperties> = {
    top: {
      top: 200,
      left: "50%",
      transform: `translateX(-50%) scale(${scale})`,
    },
    center: {
      top: "40%",
      left: "50%",
      transform: `translate(-50%, -50%) scale(${scale})`,
    },
    bottom: {
      bottom: 350,
      left: "50%",
      transform: `translateX(-50%) scale(${scale})`,
    },
  };

  return (
    <div
      style={{
        position: "absolute",
        ...positionStyles[position],
        maxWidth,
        padding: spacing.lg,
        backgroundColor: "white",
        borderRadius: borderRadius.lg,
        boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
        border: `3px solid ${sceneStyle.accentColor}`,
        opacity,
      }}
    >
      {/* Decorative corner */}
      <div
        style={{
          position: "absolute",
          top: -8,
          left: 40,
          width: 16,
          height: 16,
          backgroundColor: sceneStyle.accentColor,
          borderRadius: "50%",
        }}
      />

      <p
        style={{
          margin: 0,
          fontSize: sceneStyle.textSize,
          fontFamily: typography.fontFamily.body,
          fontWeight: typography.fontWeight.medium,
          color: colors.text.primary,
          lineHeight: typography.lineHeight.relaxed,
          textAlign: "center",
        }}
      >
        {displayText}
        {animate && visibleChars < text.length && (
          <span
            style={{
              opacity: frame % 20 > 10 ? 1 : 0,
              color: sceneStyle.accentColor,
            }}
          >
            |
          </span>
        )}
      </p>
    </div>
  );
};

// Title variant for title scenes
export const TitleText: React.FC<{
  title: string;
  subtitle?: string;
}> = ({ title, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { colors, typography, spacing } = whiteboardTheme;

  const titleScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 100 },
  });

  const subtitleOpacity = interpolate(frame, [20, 35], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: "35%",
        left: "50%",
        transform: "translate(-50%, -50%)",
        textAlign: "center",
        width: "90%",
      }}
    >
      <h1
        style={{
          margin: 0,
          marginBottom: spacing.md,
          fontSize: typography.fontSize["3xl"],
          fontFamily: typography.fontFamily.heading,
          fontWeight: typography.fontWeight.bold,
          color: colors.text.primary,
          transform: `scale(${titleScale})`,
        }}
      >
        {title}
      </h1>
      {subtitle && (
        <p
          style={{
            margin: 0,
            fontSize: typography.fontSize.lg,
            fontFamily: typography.fontFamily.body,
            fontWeight: typography.fontWeight.normal,
            color: colors.text.secondary,
            opacity: subtitleOpacity,
          }}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
};
