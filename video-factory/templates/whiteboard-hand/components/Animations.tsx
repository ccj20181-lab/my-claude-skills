import { spring, interpolate, Easing } from "remotion";

export const useWhiteboardAnimations = (frame: number, fps: number) => {
  const popIn = (delay: number) => spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 200 }
  });

  const fadeIn = (startFrame: number, duration: number = 15) =>
    interpolate(frame, [startFrame, startFrame + duration], [0, 1], { extrapolateRight: "clamp" });

  const slideUp = (startFrame: number, distance: number = 80) =>
    interpolate(frame, [startFrame, startFrame + 25], [distance, 0], {
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic)
    });

  const float = (speed: number = 0.05, amplitude: number = 8) =>
    Math.sin(frame * speed) * amplitude;

  return { popIn, fadeIn, slideUp, float };
};
