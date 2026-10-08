import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { SCENE_FRAMES as S, TOTAL_FRAMES, TRANSITION_FRAMES, C } from "./theme";
import { Background } from "./ui";
import { HookScene } from "./scenes/HookScene";
import { PurposeScene } from "./scenes/PurposeScene";
import { DataScene } from "./scenes/DataScene";
import { PythonScene } from "./scenes/PythonScene";
import { ExcelScene } from "./scenes/ExcelScene";
import { StressScene } from "./scenes/StressScene";
import { ResultScene } from "./scenes/ResultScene";
import { InsightScene } from "./scenes/InsightScene";
import { CtaScene } from "./scenes/CtaScene";

const timing = linearTiming({ durationInFrames: TRANSITION_FRAMES });

const ProgressBar: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        bottom: 0,
        height: 10,
        width: `${(frame / (TOTAL_FRAMES - 1)) * 100}%`,
        background: `linear-gradient(90deg, ${C.blue}, ${C.cyan})`,
        boxShadow: `0 0 24px ${C.cyan}`,
      }}
    />
  );
};

export const InditexVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill>
      <Background />
      <TransitionSeries>
        <TransitionSeries.Sequence name="Hook" durationInFrames={S.hook} premountFor={fps}>
          <HookScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />
        <TransitionSeries.Sequence name="Purpose" durationInFrames={S.purpose} premountFor={fps}>
          <PurposeScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={timing} />
        <TransitionSeries.Sequence name="Data" durationInFrames={S.data} premountFor={fps}>
          <DataScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />
        <TransitionSeries.Sequence name="Python" durationInFrames={S.python} premountFor={fps}>
          <PythonScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={timing} />
        <TransitionSeries.Sequence name="Excel" durationInFrames={S.excel} premountFor={fps}>
          <ExcelScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />
        <TransitionSeries.Sequence name="Stress test" durationInFrames={S.stress} premountFor={fps}>
          <StressScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={timing} />
        <TransitionSeries.Sequence name="Result" durationInFrames={S.result} premountFor={fps}>
          <ResultScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={timing} />
        <TransitionSeries.Sequence name="Insight" durationInFrames={S.insight} premountFor={fps}>
          <InsightScene />
        </TransitionSeries.Sequence>
        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={timing} />
        <TransitionSeries.Sequence name="Call to action" durationInFrames={S.cta} premountFor={fps}>
          <CtaScene />
        </TransitionSeries.Sequence>
      </TransitionSeries>
      <ProgressBar />
      {/* Música original generada con scripts/make_music.py; sus golpes están sincronizados con las animaciones. */}
      <Audio src={staticFile("music.wav")} premountFor={fps} />
    </AbsoluteFill>
  );
};
