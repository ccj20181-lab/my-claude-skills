/**
 * 品牌标识组件 - Logo + 水印
 * Branding component with logo and watermark
 */

import React from "react";
import { Img, staticFile, useCurrentFrame, interpolate } from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";

export const Branding: React.FC = () => {
  const { layout, colors, typography } = whiteboardTheme;
  const frame = useCurrentFrame();

  // 20-frame fade-in for both logo and watermark
  const logoOpacity = interpolate(frame, [0, 20], [0, 0.85], {
    extrapolateRight: "clamp",
  });
  const watermarkOpacity = interpolate(frame, [0, 20], [0, 0.6], {
    extrapolateRight: "clamp",
  });

  return (
    <>
      {/* 右上角 Logo */}
      <Img
        src={staticFile("logo.png")}
        style={{
          position: "absolute",
          top: layout.logo.top,
          right: layout.logo.right,
          width: layout.logo.width,
          height: "auto",
          objectFit: "contain",
          opacity: logoOpacity,
        }}
      />

      {/* 左下角水印 */}
      <div
        style={{
          position: "absolute",
          bottom: layout.watermark.bottom,
          left: (layout.watermark as any).left,
          fontSize: layout.watermark.fontSize,
          fontFamily: typography.fontFamily.body,
          fontWeight: typography.fontWeight.medium,
          color: colors.text.muted,
          opacity: watermarkOpacity,
        }}
      >
        @秒懂金融
      </div>
    </>
  );
};
