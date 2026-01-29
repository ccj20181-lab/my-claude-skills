// Knowledge-Explainer Template - 金融小知识科普模板
// 3:4 竖屏 (1080×1440) 专用

import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig, staticFile, interpolate, spring } from "remotion";
import React from "react";

// 视频配置
export const VIDEO_WIDTH = 1080;
export const VIDEO_HEIGHT = 1440;
export const VIDEO_FPS = 30;

// 品牌色彩
export const COLORS = {
  primary: "#1a1a2e",      // 深蓝背景
  secondary: "#16213e",    // 次要背景
  accent: "#ffd700",       // 金色强调
  text: "#ffffff",         // 白色文字
  textSecondary: "#e0e0e0", // 次要文字
  highlight: "#6c5ce7",    // 紫色高亮
};

// 字体配置
export const FONTS = {
  title: "64px",
  subtitle: "48px",
  body: "36px",
  small: "28px",
};

// 场景类型
export interface Scene {
  id: string;
  image: string;
  startFrame: number;
  durationFrames: number;
  type: "title" | "content" | "summary" | "ending";
  content: {
    mainTitle?: string;
    subTitle?: string;
    text?: string;
    points?: string[];
    highlightWords?: string[];
  };
}

// 示例场景配置 (Fallback)
export const defaultScenes: Scene[] = [
  {
    id: "opening",
    image: "scenes/scene_01.png",
    startFrame: 0,
    durationFrames: 150,
    type: "title",
    content: {
      mainTitle: "Video Factory",
      subTitle: "Template Demo"
    }
  }
];

// 标题场景组件
export const TitleScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const opacity = interpolate(progress, [0, 0.2], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(progress, [0, 0.3], [0.8, 1], { extrapolateRight: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        top: "40%",
        left: 0,
        right: 0,
        textAlign: "center",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          fontSize: FONTS.title,
          fontWeight: "bold",
          color: COLORS.accent,
          marginBottom: 20,
          textShadow: "2px 2px 8px rgba(0,0,0,0.5)",
        }}
      >
        {scene.content.mainTitle}
      </div>
      {scene.content.subTitle && (
        <div
          style={{
            fontSize: FONTS.subtitle,
            color: COLORS.text,
            textShadow: "1px 1px 4px rgba(0,0,0,0.5)",
          }}
        >
          {scene.content.subTitle}
        </div>
      )}
    </div>
  );
};

// 内容场景组件
export const ContentScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const text = scene.content.text || "";
  const charCount = Math.floor(text.length * Math.min(1, progress * 2));
  const displayText = text.substring(0, charCount);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 150,
        left: 60,
        right: 60,
        padding: 30,
        backgroundColor: "rgba(0,0,0,0.7)",
        borderRadius: 20,
        backdropFilter: "blur(10px)",
      }}
    >
      <div
        style={{
          fontSize: FONTS.body,
          color: COLORS.text,
          lineHeight: 1.6,
        }}
      >
        {displayText}
        {charCount < text.length && (
          <span style={{ opacity: 0.5 }}>|</span>
        )}
      </div>
    </div>
  );
};

// 总结场景组件
export const SummaryScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const points = scene.content.points || [];

  return (
    <div
      style={{
        position: "absolute",
        bottom: 150,
        left: 40,
        right: 40,
      }}
    >
      {points.map((point, index) => {
        const pointProgress = interpolate(
          progress,
          [index * 0.25, (index + 1) * 0.25],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );

        return (
          <div
            key={index}
            style={{
              padding: "20px 30px",
              marginBottom: 15,
              backgroundColor: "rgba(108, 92, 231, 0.9)",
              borderRadius: 15,
              opacity: pointProgress,
              transform: `translateX(${(1 - pointProgress) * 50}px)`,
            }}
          >
            <div
              style={{
                fontSize: FONTS.body,
                color: COLORS.text,
                fontWeight: "bold",
              }}
            >
              {`${index + 1}. ${point}`}
            </div>
          </div>
        );
      })}
    </div>
  );
};

// 结尾场景组件
export const EndingScene: React.FC<{ scene: Scene; progress: number }> = ({ scene, progress }) => {
  const opacity = interpolate(progress, [0, 0.3], [0, 1], { extrapolateRight: "clamp" });
  const scale = interpolate(progress, [0.7, 1], [1, 1.05], { extrapolateLeft: "clamp" });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 200,
        left: 0,
        right: 0,
        textAlign: "center",
        opacity,
        transform: `scale(${scale})`,
      }}
    >
      <div
        style={{
          fontSize: FONTS.subtitle,
          color: COLORS.accent,
          fontWeight: "bold",
          textShadow: "2px 2px 8px rgba(0,0,0,0.5)",
        }}
      >
        {scene.content.text}
      </div>
    </div>
  );
};

// 主视频组件
export const KnowledgeExplainer: React.FC<{ scenes?: Scene[] }> = ({ scenes = defaultScenes }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 查找当前场景
  const currentScene = scenes.find(
    (scene) =>
      frame >= scene.startFrame &&
      frame < scene.startFrame + scene.durationFrames
  ) || scenes[0];

  // 计算场景内进度
  const sceneProgress =
    (frame - currentScene.startFrame) / currentScene.durationFrames;

  // 根据场景类型渲染对应组件
  const renderSceneContent = () => {
    switch (currentScene.type) {
      case "title":
        return <TitleScene scene={currentScene} progress={sceneProgress} />;
      case "content":
        return <ContentScene scene={currentScene} progress={sceneProgress} />;
      case "summary":
        return <SummaryScene scene={currentScene} progress={sceneProgress} />;
      case "ending":
        return <EndingScene scene={currentScene} progress={sceneProgress} />;
      default:
        return <ContentScene scene={currentScene} progress={sceneProgress} />;
    }
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.primary,
      }}
    >
      {/* 背景图片 - 使用 staticFile 处理本地资源 */}
      <Img
        src={staticFile(currentScene.image)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
        onError={(e) => {
            console.warn(`Failed to load image: ${currentScene.image}`);
            // Fallback visualization if image fails
            (e.target as HTMLImageElement).style.display = 'none';
        }}
      />

      {/* 场景内容 */}
      {renderSceneContent()}

      {/* 品牌水印 */}
      <div
        style={{
          position: "absolute",
          top: 40,
          right: 40,
          fontSize: FONTS.small,
          color: COLORS.accent,
          opacity: 0.8,
        }}
      >
        秒懂金融
      </div>
    </AbsoluteFill>
  );
};

export default KnowledgeExplainer;
