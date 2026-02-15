/**
 * Remotion Root - 注册视频组合
 *
 * 动态从 data.json 加载视频数据
 */
import React from "react";
import { Composition } from "remotion";
import { VideoComposition } from "./Composition";
import { VideoData } from "./types/scene";

// 导入 data.json - Remotion 支持直接导入 JSON
// 这个文件会被 Python 脚本动态更新
import videoData from "./data.json";

// 类型断言
const typedVideoData = videoData as VideoData;

export const RemotionRoot: React.FC = () => {
  // 计算总帧数
  const sceneFrames = typedVideoData.scenes.reduce(
    (acc, scene) => acc + Math.round(scene.duration * 30),
    0
  );
  const outroFrames =
    typedVideoData.book_outro?.enabled
      ? Math.round((typedVideoData.book_outro.duration || 0) * 30)
      : 0;
  const totalFrames = sceneFrames + outroFrames;

  return (
    <>
      <Composition
        id="FinanceVideo"
        component={VideoComposition}
        durationInFrames={totalFrames || 3600} // 默认120秒
        fps={typedVideoData.meta.fps || 30}
        width={typedVideoData.meta.width || 1080}
        height={typedVideoData.meta.height || 1440}
        defaultProps={{
          data: typedVideoData,
        }}
      />
    </>
  );
};

export default RemotionRoot;
