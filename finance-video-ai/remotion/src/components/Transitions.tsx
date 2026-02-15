/**
 * 转场效果组件
 */
import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";

type TransitionType =
  | "fade"
  | "zoom"
  | "slideUp"
  | "slideDown"
  | "slideLeft"
  | "slideRight"
  | "scaleFromCenter"
  | "wipe";

interface TransitionProps {
  type: TransitionType;
  duration: number;
  durationInFrames: number;
  children: React.ReactNode;
}

export const Transition: React.FC<TransitionProps> = ({
  type,
  duration,
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const { width, height } = { width: 1080, height: 1440 };

  // 入场动画 (0 到 duration 帧)
  const entryProgress = interpolate(frame, [0, duration], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // 出场动画 (最后 duration 帧)
  const exitStart = durationInFrames - duration;
  const exitProgress = interpolate(
    frame,
    [exitStart, durationInFrames],
    [1, 0],
    {
      extrapolateRight: "clamp",
      extrapolateLeft: "clamp",
      easing: Easing.in(Easing.cubic),
    }
  );

  // 组合入场和出场
  const progress = frame < exitStart ? entryProgress : exitProgress;

  const getTransitionStyle = (): React.CSSProperties => {
    switch (type) {
      case "fade":
        return {
          opacity: progress,
        };

      case "zoom":
        return {
          opacity: progress,
          transform: `scale(${0.8 + progress * 0.2})`,
        };

      case "slideUp":
        return {
          opacity: progress,
          transform: `translateY(${(1 - progress) * 100}px)`,
        };

      case "slideDown":
        return {
          opacity: progress,
          transform: `translateY(${(1 - progress) * -100}px)`,
        };

      case "slideLeft":
        return {
          opacity: progress,
          transform: `translateX(${(1 - progress) * 100}px)`,
        };

      case "slideRight":
        return {
          opacity: progress,
          transform: `translateX(${(1 - progress) * -100}px)`,
        };

      case "scaleFromCenter":
        return {
          opacity: progress,
          transform: `scale(${0.5 + progress * 0.5})`,
        };

      case "wipe":
        return {
          clipPath: `inset(0 ${(1 - progress) * 100}% 0 0)`,
        };

      default:
        return {
          opacity: progress,
        };
    }
  };

  return (
    <AbsoluteFill style={getTransitionStyle()}>
      {children}
    </AbsoluteFill>
  );
};
