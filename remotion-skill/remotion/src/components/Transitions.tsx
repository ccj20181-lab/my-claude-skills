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

type TransitionType = "fade" | "slideLeft" | "slideRight" | "slideUp" | "slideDown" | "wipe" | "zoom" | "flipY" | "scaleFromCenter";

interface TransitionProps {
  type: TransitionType;
  duration?: number;
  exitDuration?: number;
  durationInFrames?: number;
  direction?: "in" | "out";
  children: React.ReactNode;
}

export const Transition: React.FC<TransitionProps> = ({
  type,
  duration = 15,
  exitDuration = 10,
  durationInFrames,
  direction = "in",
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance progress
  const enterProgress = interpolate(frame, [0, duration], [0, 1], {
    extrapolateRight: "clamp",
  });

  const enterSpring = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 120 },
  });

  // Exit progress (fade/slide out at end of scene)
  let exitProgress = 1; // 1 = fully visible
  if (durationInFrames && durationInFrames > 0) {
    const exitStart = Math.max(0, durationInFrames - exitDuration);
    // Ensure strictly monotonically increasing inputRange
    if (exitStart < durationInFrames) {
      exitProgress = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
    }
  }

  const getEnterStyle = (): React.CSSProperties => {
    switch (type) {
      case "fade":
        return {
          opacity: enterProgress,
        };

      case "slideLeft":
        return {
          opacity: enterProgress,
          transform: `translateX(${(1 - enterSpring) * 100}px)`,
        };

      case "slideRight":
        return {
            opacity: enterProgress,
            transform: `translateX(${-(1 - enterSpring) * 100}px)`,
        };

      case "slideUp":
        return {
          opacity: enterProgress,
          transform: `translateY(${(1 - enterSpring) * 50}px)`,
        };

      case "slideDown":
          return {
              opacity: enterProgress,
              transform: `translateY(${-(1 - enterSpring) * 50}px)`,
          };

      case "wipe":
        // Diagonal wipe from top-left
        return {
          clipPath: `polygon(0 0, ${enterProgress * 150}% 0, ${enterProgress * 150 - 50}% 100%, 0 100%)`,
        };

      case "zoom":
        return {
          opacity: enterProgress,
          transform: `scale(${0.9 + enterSpring * 0.1})`,
        };

      case "flipY":
        return {
          opacity: enterProgress,
          transform: `perspective(1000px) rotateY(${(1 - enterSpring) * 90}deg)`,
        };

      case "scaleFromCenter":
        return {
          opacity: enterProgress,
          transform: `scale(${0.7 + enterSpring * 0.3})`,
          transformOrigin: "center center",
        };

      default:
        return { opacity: enterProgress };
    }
  };

  const enterStyle = getEnterStyle();

  // Combine enter and exit: multiply opacity, add exit slide
  const exitSlideY = exitProgress < 1
    ? interpolate(exitProgress, [0, 1], [-20, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;

  const combinedStyle: React.CSSProperties = {
    ...enterStyle,
    opacity: ((enterStyle.opacity as number) ?? 1) * exitProgress,
  };

  // Add exit slide to existing transform if present
  if (exitProgress < 1 && enterStyle.transform) {
    combinedStyle.transform = `${enterStyle.transform} translateY(${exitSlideY}px)`;
  } else if (exitProgress < 1) {
    combinedStyle.transform = `translateY(${exitSlideY}px)`;
  }

  return (
    <AbsoluteFill style={combinedStyle}>
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
