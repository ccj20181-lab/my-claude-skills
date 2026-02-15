/**
 * 品牌标识组件 - Logo + 水印
 * Branding component with logo and watermark
 * 适配 minimalist 主题
 */

import React from "react";
import { Img, staticFile } from "remotion";
import { minimalistTheme } from "../theme/minimalist";

export const Branding: React.FC = () => {
  const { layout, colors, typography } = minimalistTheme;

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
          opacity: 1,
        }}
      />

      {/* 左下角水印 */}
      <div
        style={{
          position: "absolute",
          bottom: 30,
          left: 60,
          fontSize: 18,
          fontFamily: typography.fontFamily,
          fontWeight: 500,
          color: colors.secondary,
          opacity: 1,
        }}
      >
        @秒懂金融
      </div>
    </>
  );
};
