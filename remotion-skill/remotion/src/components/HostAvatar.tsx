/**
 * 主持人形象（替代火柴人体系）
 * Simple host avatar built with SVG. No external assets required.
 */

import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";

type Emotion =
  | "thinking"
  | "happy"
  | "confused"
  | "pointing"
  | "waving"
  | "surprised"
  | "neutral"
  | string;

export const HostAvatar: React.FC<{
  emotion?: Emotion;
  position?: "bottom-left" | "bottom-right";
  size?: number;
}> = ({ emotion = "neutral", position = "bottom-left", size = 260 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { layout } = whiteboardTheme;

  const enter = spring({
    frame,
    fps,
    config: { damping: 18, stiffness: 120 },
  });

  const bob = Math.sin(frame / 18) * 5;
  const opacity = interpolate(frame, [0, 10], [0, 1], {
    extrapolateRight: "clamp",
  });

  const base: React.CSSProperties =
    position === "bottom-right"
      ? {
          right: layout.padding.horizontal,
          bottom: layout.padding.vertical + 110,
        }
      : {
          left: layout.padding.horizontal,
          bottom: layout.padding.vertical + 110,
        };

  return (
    <div
      style={{
        position: "absolute",
        width: size,
        height: size,
        opacity,
        transform: `translateY(${(1 - enter) * 40 + bob}px)`,
        ...base,
      }}
    >
      <AvatarSVG emotion={emotion} />
    </div>
  );
};

const AvatarSVG: React.FC<{ emotion: Emotion }> = ({ emotion }) => {
  const frame = useCurrentFrame();
  const skin = "#F6D7B8";
  const hair = "#2D3748";
  const shirt = "#3182CE";
  const outline = "#1A202C";

  // Simple blink: close eyes briefly every ~3-4 seconds.
  const t = (frame + 17) % 110;
  const blink = t >= 0 && t < 4;

  const mouth = (() => {
    switch (emotion) {
      case "happy":
        return <path d="M 62 86 Q 80 102 98 86" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />;
      case "surprised":
        return <ellipse cx="80" cy="92" rx="10" ry="12" fill="#fff" stroke={outline} strokeWidth={4} />;
      case "confused":
        return <path d="M 62 92 Q 70 86 80 92 Q 90 98 98 92" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />;
      case "thinking":
        return <path d="M 66 94 Q 80 90 94 94" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />;
      default:
        return <path d="M 66 94 Q 80 96 94 94" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />;
    }
  })();

  const eyebrows = (() => {
    switch (emotion) {
      case "confused":
        return (
          <>
            <path d="M 50 64 Q 62 58 72 64" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />
            <path d="M 88 66 Q 98 62 110 66" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />
          </>
        );
      case "surprised":
        return (
          <>
            <path d="M 50 58 Q 62 54 74 58" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />
            <path d="M 86 58 Q 98 54 110 58" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />
          </>
        );
      default:
        return (
          <>
            <path d="M 50 62 Q 62 60 74 62" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />
            <path d="M 86 62 Q 98 60 110 62" stroke={outline} strokeWidth={4} fill="none" strokeLinecap="round" />
          </>
        );
    }
  })();

  const gesture = (() => {
    // Minimal gesture hint: a small hand wave / point icon.
    if (emotion === "waving") {
      const wave = Math.sin(frame / 6) * 6;
      return <path d={`M 150 165 Q ${168 + wave} ${140 - wave} 186 165`} stroke={outline} strokeWidth={6} fill="none" strokeLinecap="round" />;
    }
    if (emotion === "pointing") {
      const point = Math.sin(frame / 10) * 4;
      return <path d={`M 150 165 Q ${176 + point} ${156 - point} 202 152`} stroke={outline} strokeWidth={6} fill="none" strokeLinecap="round" />;
    }
    return null;
  })();

  return (
    <svg viewBox="0 0 220 220" width="100%" height="100%">
      {/* Body */}
      <path
        d="M 60 210 Q 110 150 160 210 Z"
        fill={shirt}
        stroke={outline}
        strokeWidth={6}
        strokeLinejoin="round"
      />

      {/* Neck */}
      <rect x="96" y="122" width="28" height="30" rx="12" fill={skin} stroke={outline} strokeWidth={6} />

      {/* Head */}
      <circle cx="110" cy="90" r="60" fill={skin} stroke={outline} strokeWidth={6} />

      {/* Hair */}
      <path
        d="M 54 78 Q 64 30 110 30 Q 170 30 170 90 Q 148 66 110 64 Q 82 64 54 78 Z"
        fill={hair}
        stroke={outline}
        strokeWidth={6}
        strokeLinejoin="round"
      />

      {/* Eyes */}
      {blink ? (
        <>
          <path d="M 76 84 Q 86 88 96 84" stroke={outline} strokeWidth={6} fill="none" strokeLinecap="round" />
          <path d="M 124 84 Q 134 88 144 84" stroke={outline} strokeWidth={6} fill="none" strokeLinecap="round" />
        </>
      ) : (
        <>
          <circle cx="86" cy="84" r="8" fill={outline} />
          <circle cx="134" cy="84" r="8" fill={outline} />
        </>
      )}

      {/* Eyebrows */}
      {eyebrows}

      {/* Cheeks */}
      <ellipse cx="66" cy="100" rx="12" ry="8" fill="#FFB3C1" opacity="0.45" />
      <ellipse cx="154" cy="100" rx="12" ry="8" fill="#FFB3C1" opacity="0.45" />

      {/* Mouth */}
      {mouth}

      {/* Simple arm + gesture */}
      <path d="M 70 165 Q 52 156 44 146" stroke={outline} strokeWidth={6} fill="none" strokeLinecap="round" />
      <path d="M 150 165 Q 164 150 180 140" stroke={outline} strokeWidth={6} fill="none" strokeLinecap="round" />
      {gesture}
    </svg>
  );
};
