import { Composition } from "remotion";
import { MainComposition } from "./Composition";
import { whiteboardTheme } from "./whiteboard-theme";
import data from "./data.json";
import React from "react";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="WhiteboardVideo"
        component={MainComposition}
        durationInFrames={data.totalFrames || 900}
        fps={data.fps || 30}
        width={1080}
        height={1440}
        defaultProps={{}}
      />
    </>
  );
};
