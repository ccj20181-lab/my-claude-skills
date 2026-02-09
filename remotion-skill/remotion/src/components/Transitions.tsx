/**
 * 转场动画组件
 * Transition animations between scenes
 */

import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  AbsoluteFill,
} from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";

type TransitionType = "fade" | "slideLeft" | "slideUp" | "wipe" | "zoom";

interface TransitionProps {
  type: TransitionType;
  duration?: number;
  direction?: "in" | "out";
  children: React.ReactNode;
}

export const Transition: React.FC<TransitionProps> = ({
  type,
  duration = 15,
  direction = "in",
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress =
    direction === "in"
      ? interpolate(frame, [0, duration], [0, 1], {
          extrapolateRight: "clamp",
        })
      : interpolate(frame, [0, duration], [1, 0], {
          extrapolateRight: "clamp",
        });

  const springProgress = spring({
    frame: direction === "in" ? frame : duration - frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  const getTransformStyle = (): React.CSSProperties => {
    switch (type) {
      case "fade":
        return {
          opacity: progress,
        };

      case "slideLeft":
        return {
          opacity: progress,
          transform: `translateX(${(1 - springProgress) * 100}px)`,
        };

      case "slideUp":
        return {
          opacity: progress,
          transform: `translateY(${(1 - springProgress) * 50}px)`,
        };

      case "wipe":
        return {
          clipPath: `inset(0 ${(1 - progress) * 100}% 0 0)`,
        };

      case "zoom":
        return {
          opacity: progress,
          transform: `scale(${0.9 + springProgress * 0.1})`,
        };

      default:
        return { opacity: progress };
    }
  };

  return (
    <AbsoluteFill style={getTransformStyle()}>
      {children}
    </AbsoluteFill>
  );
};

// Scene transition overlay
export const SceneTransition: React.FC<{
  color?: string;
  duration?: number;
}> = ({ color = "#FFFFFF", duration = 10 }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(
    frame,
    [0, duration / 2, duration],
    [0, 1, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: color,
        opacity,
        pointerEvents: "none",
      }}
    />
  );
};

// Stagger animation for list items
export const StaggerContainer: React.FC<{
  children: React.ReactNode[];
  staggerDelay?: number;
}> = ({ children, staggerDelay = 8 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      {React.Children.map(children, (child, index) => {
        const delay = index * staggerDelay;
        const adjustedFrame = Math.max(0, frame - delay);

        const opacity = interpolate(adjustedFrame, [0, 10], [0, 1], {
          extrapolateRight: "clamp",
        });

        const translateY = spring({
          frame: adjustedFrame,
          fps,
          config: { damping: 15, stiffness: 120 },
        });

        return (
          <div
            style={{
              opacity,
              transform: `translateY(${(1 - translateY) * 20}px)`,
            }}
          >
            {child}
          </div>
        );
      })}
    </>
  );
};
