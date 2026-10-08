import React from "react";
import { Composition } from "remotion";
import { InditexVideo } from "./InditexVideo";
import { TOTAL_FRAMES } from "./theme";

// Formato 4:5 (1080x1350) a 30 fps. La duración (TOTAL_FRAMES) suma las escenas menos las transiciones: ~59 s.
export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="InditexVideo"
      component={InditexVideo}
      durationInFrames={TOTAL_FRAMES}
      fps={30}
      width={1080}
      height={1350}
    />
  );
};
