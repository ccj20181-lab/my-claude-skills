import React, { useMemo } from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

type CharacterEmotion =
  | "happy"
  | "thinking"
  | "confused"
  | "surprised"
  | "waving"
  | "pointing"
  | "neutral"
  | string;

interface CharacterProps {
  type?: CharacterEmotion;
  position?: "bottom-left" | "bottom-right";
  size?: number;
  entranceDelay?: number;
  durationInFrames?: number;
}

export const Character: React.FC<CharacterProps> = ({
  type = "neutral",
  position = "bottom-left",
  size = 300,
  entranceDelay = 8,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Delayed entrance animation (Spring Pop)
  const delayedFrame = Math.max(0, frame - entranceDelay);
  const scale = spring({
    frame: delayedFrame,
    fps,
    config: {
      damping: 12,
      stiffness: 200,
      mass: 0.8,
    },
  });

  // Exit animation: fade out + slide down in last 15 frames
  let exitOpacity = 1;
  let exitSlide = 0;
  if (durationInFrames && durationInFrames > 0) {
    const exitStart = durationInFrames - 15;
    exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
    exitSlide = interpolate(frame, [exitStart, durationInFrames], [0, 30], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  }

  // Entrance opacity
  const entranceOpacity = interpolate(delayedFrame, [0, 8], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Breathing animation (Continuous sine wave)
  const breathe = Math.sin(frame / 45) * 0.02;

  // Slight floating/wiggle
  const float = Math.sin(frame / 60) * 5;

  // Eye blinking logic
  const blinkCycle = frame % 150;
  const isBlinking = blinkCycle > 140 && blinkCycle < 145;

  const style: React.CSSProperties = useMemo(() => {
    const baseStyle: React.CSSProperties = {
      position: "absolute",
      bottom: 340,
      width: size,
      height: size,
      transformOrigin: "bottom center",
    };

    if (position === "bottom-left") {
      baseStyle.left = 50;
    } else {
      baseStyle.right = 50;
      baseStyle.transform = "scaleX(-1)";
    }

    return baseStyle;
  }, [position, size]);

  // SVG Paths for different emotions
  const strokeColor = "#1A202C";
  const strokeWidth = 5;

  return (
    <div style={{
      ...style,
      transform: `${style.transform || ''} translateY(${-float + exitSlide}px) scale(${scale * (1 + breathe)})`,
      opacity: entranceOpacity * exitOpacity,
    }}>
      <svg viewBox="0 0 200 200" width="100%" height="100%" style={{ overflow: "visible" }}>
        {/* Shadow */}
        <ellipse cx="100" cy="190" rx="40" ry="8" fill="rgba(0,0,0,0.1)" />

        {/* Body (Cute rounded shape) */}
        <path
          d="M 100 130 C 100 130, 80 180, 80 180 M 100 130 C 100 130, 120 180, 120 180"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
        />
        <path
          d="M 100 130 L 100 90"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
        />

        {/* Arms */}
        {renderArms(type, strokeColor, strokeWidth, frame)}

        {/* Head */}
        <circle cx="100" cy="70" r="35" fill="white" stroke={strokeColor} strokeWidth={strokeWidth} />

        {/* Face */}
        <g transform="translate(100, 70)">
           {renderFace(type, strokeColor, isBlinking)}
        </g>
      </svg>
    </div>
  );
};

// Helper to render arms based on emotion/type
function renderArms(type: string, color: string, width: number, frame: number) {
  const wave = Math.sin(frame / 10) * 10;

  switch (type) {
    case "waving":
      return (
        <>
          <path d="M 100 100 L 70 130" stroke={color} strokeWidth={width} strokeLinecap="round" />
          <path d={`M 100 100 L 140 ${80 + wave}`} stroke={color} strokeWidth={width} strokeLinecap="round" />
        </>
      );
    case "pointing":
      return (
        <>
           <path d="M 100 100 L 70 130" stroke={color} strokeWidth={width} strokeLinecap="round" />
           <path d="M 100 100 L 150 90" stroke={color} strokeWidth={width} strokeLinecap="round" />
        </>
      );
    case "thinking":
      return (
        <>
           <path d="M 100 100 L 70 130" stroke={color} strokeWidth={width} strokeLinecap="round" />
           <path d="M 100 100 L 120 60" stroke={color} strokeWidth={width} strokeLinecap="round" />
        </>
      );
    case "confused":
       return (
        <>
           <path d="M 100 100 L 70 90" stroke={color} strokeWidth={width} strokeLinecap="round" />
           <path d="M 100 100 L 130 90" stroke={color} strokeWidth={width} strokeLinecap="round" />
        </>
      );
    default: // Neutral/Happy
      return (
        <>
          <path d="M 100 100 L 70 130" stroke={color} strokeWidth={width} strokeLinecap="round" />
          <path d="M 100 100 L 130 130" stroke={color} strokeWidth={width} strokeLinecap="round" />
        </>
      );
  }
}

// Helper to render face
function renderFace(type: string, color: string, blinking: boolean) {
  // Eyes
  const leftEye = blinking
    ? <path d="M -15 -5 L -5 -5" stroke={color} strokeWidth={3} strokeLinecap="round" />
    : <circle cx="-10" cy="-5" r="3" fill={color} />;

  const rightEye = blinking
    ? <path d="M 5 -5 L 15 -5" stroke={color} strokeWidth={3} strokeLinecap="round" />
    : <circle cx="10" cy="-5" r="3" fill={color} />;

  // Mouth & Extras
  let mouth;
  let extras = null;

  switch (type) {
    case "happy":
    case "waving":
    case "pointing":
      mouth = <path d="M -10 10 Q 0 20 10 10" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" />;
      break;
    case "surprised":
      mouth = <circle cx="0" cy="15" r="5" fill="none" stroke={color} strokeWidth={3} />;
      break;
    case "thinking":
      mouth = <line x1="-5" y1="15" x2="5" y2="15" stroke={color} strokeWidth={3} strokeLinecap="round" />;
      extras = (
        <g>
          <circle cx="35" cy="-35" r="3" fill={color} opacity="0.5" />
          <circle cx="45" cy="-45" r="5" fill={color} opacity="0.5" />
        </g>
      );
      break;
    case "confused":
      mouth = <path d="M -8 15 Q 0 10 8 15" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" />;
      extras = <text x="25" y="-20" fontSize="30" fill={color} fontWeight="bold">?</text>;
      break;
    default:
      mouth = <path d="M -5 15 Q 0 18 5 15" fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" />;
  }

  return (
    <>
      {leftEye}
      {rightEye}
      {mouth}
      {extras}
    </>
  );
}
