/**
 * 素材云：辅助素材以低透明度漂浮，增加画面信息密度与层次
 */

import React from "react";
import { Img, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { IconInfo, SceneType } from "../types/scene";

const float = (frame: number, speed: number, amp: number) =>
  Math.sin(frame / speed) * amp;

export const IconCloud: React.FC<{
  sceneType?: SceneType;
  icons: IconInfo[];
  opacity?: number;
}> = ({ sceneType, icons, opacity = 0.22 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Repositioned slots: spread around edges to avoid hero zone overlap
  const slots: Array<{ x: number; y: number; s: number; r: number }> =
    sceneType === "title"
      ? [
          { x: 80,  y: 220, s: 200, r: -10 },
          { x: 800, y: 220, s: 210, r: 10 },
          { x: 80,  y: 520, s: 180, r: 8 },
          { x: 810, y: 540, s: 190, r: -8 },
        ]
      : [
          // Top-left, top-right, mid-left, mid-right, bottom-right, top-center
          { x: 60,  y: 130, s: 200, r: -10 },
          { x: 810, y: 120, s: 210, r: 10 },
          { x: 40,  y: 460, s: 180, r: 8 },
          { x: 830, y: 440, s: 190, r: -8 },
          { x: 800, y: 720, s: 170, r: -6 },
          { x: 440, y: 120, s: 160, r: 6 },
        ];

  const safeIcons = icons.filter((i) => i?.path).slice(0, slots.length);
  if (safeIcons.length === 0) return null;

  return (
    <>
      {safeIcons.map((icon, idx) => {
        const slot = slots[idx];
        const dy = float(frame + idx * 13, 22 + idx * 3, 10 + idx * 2);
        const dx = float(frame + idx * 29, 31 + idx * 2, 8);
        const enter = spring({
          frame: Math.max(0, frame - idx * 6),
          fps,
          config: { damping: 18, stiffness: 120 },
        });

        // Pulse breathing effect
        const pulse = 1 + Math.sin(frame / 50 + idx * 1.5) * 0.03;
        // Micro rotation animation
        const rotate = slot.r + Math.sin(frame / 40 + idx * 2) * 2;

        return (
          <Img
            key={`${icon.name}-${idx}`}
            src={staticFile(icon.path as string)}
            style={{
              position: "absolute",
              left: slot.x + dx,
              top: slot.y + dy,
              width: slot.s,
              height: "auto",
              opacity: opacity * (0.65 + enter * 0.35),
              transform: `rotate(${rotate}deg) scale(${(0.92 + enter * 0.08) * pulse})`,
              filter: "grayscale(0.06) drop-shadow(0 8px 18px rgba(0,0,0,0.08))",
            }}
          />
        );
      })}
    </>
  );
};
