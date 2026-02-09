/**
 * Remotion 入口文件
 * Root composition for Miaodong Finance Video
 */

import { Composition } from "remotion";
import { MiaodongVideo } from "./Composition";
import { whiteboardTheme } from "./theme/whiteboard";
import videoData from "./data.json";
import type { VideoData } from "./types/scene";

export const RemotionRoot: React.FC = () => {
  const { layout } = whiteboardTheme;
  const typedVideoData = videoData as unknown as VideoData;

  // Calculate total duration from actual data.json scenes
  const totalDuration = typedVideoData.scenes.reduce(
    (sum, scene) => sum + Math.ceil(scene.duration * typedVideoData.meta.fps),
    0
  );

  return (
    <>
      <Composition<any, { data: VideoData }>
        id="MiaodongVideo"
        component={MiaodongVideo}
        durationInFrames={totalDuration}
        fps={typedVideoData.meta.fps}
        width={layout.width}
        height={layout.height}
        defaultProps={{
          data: typedVideoData,
        }}
      />
    </>
  );
};
