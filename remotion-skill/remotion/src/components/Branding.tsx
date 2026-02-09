/**
 * 品牌标识组件 - Logo + 水印
 * Branding component with logo and watermark
 */

import React from "react";
import { Img, staticFile } from "remotion";
import { whiteboardTheme } from "../theme/whiteboard";

export const Branding: React.FC = () => {
  const { layout, colors, typography } = whiteboardTheme;

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
        }}
      />

      {/* 右下角水印 */}
      <div
        style={{
          position: "absolute",
          bottom: layout.watermark.bottom,
          right: layout.watermark.right,
          fontSize: layout.watermark.fontSize,
          fontFamily: typography.fontFamily.body,
          fontWeight: typography.fontWeight.medium,
          color: colors.text.muted,
        }}
      >
        @秒懂金融
      </div>
    </>
  );
};
