/**
 * 主合成组件
 * Main composition that renders all scenes
 */

import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { VideoData } from "./types/scene";
import { Scene } from "./components/Scene";
import { whiteboardTheme } from "./theme/whiteboard";

interface MiaodongVideoProps {
  data: VideoData;
}

export const MiaodongVideo: React.FC<MiaodongVideoProps> = ({ data }) => {
  const { fps } = data.meta;

  // Calculate frame offsets for each scene
  let currentFrame = 0;
  const sceneSequences = data.scenes.map((scene) => {
    const durationInFrames = Math.ceil(scene.duration * fps);
    const startFrame = currentFrame;
    currentFrame += durationInFrames;

    // Get audio path for this scene if available
    const audioPath = data.audio?.files[scene.id]?.path;

    return (
      <Sequence
        key={scene.id}
        from={startFrame}
        durationInFrames={durationInFrames}
        name={`${scene.type}: ${scene.text.slice(0, 20)}...`}
      >
        <Scene
          data={scene}
          meta={data.meta}
          audioPath={audioPath}
          durationInFrames={durationInFrames}
          showSubtitle={true}
        />
      </Sequence>
    );
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: whiteboardTheme.colors.background,
      }}
    >
      {sceneSequences}
    </AbsoluteFill>
  );
};
