import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
} from "remotion";

/**
 * Whiteboard Animation Hooks
 * Provides hand-drawn style animations like pop-in, slide-up, etc.
 */
export const useWhiteboardAnimations = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 1. Elastic Pop-in (Standard)
  const popIn = (delay: number, config = { damping: 12, stiffness: 200 }) => {
    return spring({
      frame: frame - delay,
      fps,
      config,
    });
  };

  // 2. Soft Pop-in (Gentler)
  const softPop = (delay: number) => popIn(delay, { damping: 15, stiffness: 120 });

  // 3. Fade In
  const fadeIn = (startFrame: number, duration: number = 15) => {
    return interpolate(frame, [startFrame, startFrame + duration], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    });
  };

  // 4. Slide Up
  const slideUp = (startFrame: number, distance: number = 80) => {
    return interpolate(frame, [startFrame, startFrame + 25], [distance, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
  };

  // 5. Slide Right
  const slideRight = (startFrame: number, distance: number = 100) => {
    return interpolate(frame, [startFrame, startFrame + 25], [-distance, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
  };

  // 6. Typewriter Effect
  const typewriter = (text: string, startFrame: number, charsPerFrame: number = 0.8) => {
    const elapsed = Math.max(0, frame - startFrame);
    const visibleChars = Math.floor(elapsed * charsPerFrame);
    return text.slice(0, visibleChars);
  };

  // 7. Continuous Float
  const float = (speed: number = 0.05, amplitude: number = 8) => {
    return Math.sin(frame * speed) * amplitude;
  };

  // 8. Continuous Rotate
  const rotate = (speed: number = 0.03, amplitude: number = 5) => {
    return Math.sin(frame * speed) * amplitude;
  };

  // 9. Pulse
  const pulse = (speed: number = 0.08, min: number = 0.95, max: number = 1.05) => {
    const t = (Math.sin(frame * speed) + 1) / 2;
    return min + t * (max - min);
  };

  return {
    popIn,
    softPop,
    fadeIn,
    slideUp,
    slideRight,
    typewriter,
    float,
    rotate,
    pulse,
  };
};
