import { AbsoluteFill, Sequence } from "remotion";
import { whiteboardTheme } from "../styles/whiteboard-theme";
import { Scene1 } from "./scenes/test-video/Scene1";
import { Scene2 } from "./scenes/test-video/Scene2";

export const TestVideoComposition = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: whiteboardTheme.colors.background }}>
      <Sequence from={0} durationInFrames={150}>
        <Scene1 />
      </Sequence>
      <Sequence from={150} durationInFrames={150}>
        <Scene2 />
      </Sequence>
    </AbsoluteFill>
  );
};
