/**
 * 视频组合组件
 */
import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile } from "remotion";
import { VideoData } from "./types/scene";
import { SceneComponent } from "./components/Scene";
import { Branding } from "./components/Branding";

interface CompositionProps {
  data: VideoData;
}

export const VideoComposition: React.FC<CompositionProps> = ({ data }) => {
  const fps = data.meta.fps || 30;
  let currentFrame = 0;
  const outro = data.book_outro;
  const outroFrames = outro?.enabled ? Math.round((outro.duration || 0) * fps) : 0;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#FFFFFF",
        width: data.meta.width,
        height: data.meta.height,
      }}
    >
      {data.scenes.map((scene, index) => {
        const durationInFrames = Math.round(scene.duration * fps);
        const startFrame = currentFrame;
        currentFrame += durationInFrames;

        return (
          <Sequence
            key={scene.id}
            from={startFrame}
            durationInFrames={durationInFrames}
          >
            <SceneComponent
              data={scene}
              startFrame={0}
              durationInFrames={durationInFrames}
            />
          </Sequence>
        );
      })}

      {outro?.enabled && outroFrames > 0 && (
        <Sequence from={currentFrame} durationInFrames={outroFrames}>
          <AbsoluteFill
            style={{
              backgroundColor: "#FFFFFF",
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              padding: "80px 80px 140px 80px",
              boxSizing: "border-box",
            }}
          >
            <Img
              src={staticFile(outro.image)}
              style={{
                width: "66%",
                maxWidth: "720px",
                height: "auto",
                objectFit: "contain",
              }}
            />
            <div
              style={{
                marginTop: 28,
                fontSize: 34,
                lineHeight: 1.4,
                color: "#444",
                letterSpacing: "0.5px",
                textAlign: "center",
                fontFamily:
                  "\"PingFang SC\", \"Microsoft YaHei\", \"Noto Sans SC\", sans-serif",
              }}
            >
              {outro.text}
            </div>
          </AbsoluteFill>
        </Sequence>
      )}

      {/* Logo - 始终固定在最上层 */}
      <Branding />
    </AbsoluteFill>
  );
};

export default VideoComposition;
