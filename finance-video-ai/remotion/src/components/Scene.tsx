/**
 * 简化版场景组件
 * 仅展示AI生成的插画 + 字幕，无火柴人角色
 */
import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  staticFile,
  useCurrentFrame,
  spring,
  Sequence,
} from "remotion";
import { Scene as SceneType, SCENE_TRANSITIONS } from "../types/scene";
import { Subtitle } from "./Subtitle";
import { Transition } from "./Transitions";
import { minimalistTheme } from "../theme/minimalist";

interface SceneProps {
  data: SceneType;
  startFrame: number;
  durationInFrames: number;
  showSubtitle?: boolean;
}

export const SceneComponent: React.FC<SceneProps> = ({
  data,
  startFrame,
  durationInFrames,
  showSubtitle = true,
}) => {
  const frame = useCurrentFrame();
  const fps = 30;

  // 图片入场动画
  const imageOpacity = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  const imageScale = spring({
    frame,
    fps,
    config: { damping: 12, stiffness: 80 },
  });

  // 转场类型
  const transitionType = SCENE_TRANSITIONS[data.type] || "fade";

  return (
    <Sequence from={startFrame} durationInFrames={durationInFrames}>
      <Transition
        type={transitionType as any}
        duration={6}
        durationInFrames={durationInFrames}
      >
        <AbsoluteFill
          style={{
            backgroundColor: minimalistTheme.colors.background,
          }}
        >
          {/* AI生成的场景插画 */}
          <div
            style={{
              position: "absolute",
              width: "100%",
              height: "100%",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              padding: "20px 30px",
            }}
          >
            <Img
              src={staticFile(data.image)}
              style={{
                maxWidth: "120%",
                maxHeight: "120%",
                objectFit: "contain",
                opacity: imageOpacity,
                transform: `scale(${0.95 + imageScale * 0.05})`,
              }}
            />
          </div>

          {/* 字幕 */}
          {showSubtitle && (
            <Subtitle
              text={data.text}
              durationInFrames={durationInFrames}
              wordTimestamps={data.audio?.word_timestamps}
              accentColor={minimalistTheme.colors.accent}
              style="compact"
            />
          )}

          {/* 音频 */}
          {data.audio && <Audio src={staticFile(data.audio.path)} />}
        </AbsoluteFill>
      </Transition>
    </Sequence>
  );
};

// 默认导出
export default SceneComponent;
