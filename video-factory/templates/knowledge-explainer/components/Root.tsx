import { Composition } from "remotion";
import { KnowledgeExplainer, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS } from "./Composition";
import data from "./data.json";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="KnowledgeExplainer"
        component={KnowledgeExplainer}
        durationInFrames={data.totalFrames}
        fps={data.fps || VIDEO_FPS}
        width={VIDEO_WIDTH}
        height={VIDEO_HEIGHT}
        defaultProps={{
          scenes: data.scenes as any,
        }}
      />
    </>
  );
};
