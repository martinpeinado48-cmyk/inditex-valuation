# Inditex valuation: explainer video

A 59-second video (4:5, 1080×1350, 30 fps) that summarises the project: where the data comes from, what Excel and Python do, the stress tests and the conclusion. It is written as code with [Remotion](https://www.remotion.dev) (React), using the **real figures of the model**, and it was built with Claude Code. The soundtrack is original: it is synthesised by a Python script, so there are no third-party music rights.

Educational project, not investment advice. Figures are as of 7 October 2026.

## What is inside

```
src/
  InditexVideo.tsx         Timeline: nine scenes joined by slide transitions, background, progress bar, music
  theme.ts                 Colours, fonts, scene durations
  anim.ts, ui.tsx          Animation helpers and shared components (glass panels, pop-in text, backdrop)
  scenes/                  Hook, Purpose, Data sources, Python, Excel, Stress test, Result, Insight, Call to action
  data/modelData.json      Real figures exported from the Python model (DCF scenarios, Monte Carlo histogram, peers, Altman/Beneish)
scripts/
  export_video_data.py     Regenerates modelData.json from ../src/dcf_model.py and ../src/montecarlo.py
  make_music.py            Composes the soundtrack (numpy only): 120 BPM, A minor, effects placed frame by frame
  stills.mjs               Renders single frames to PNG to review the layout
```

## Run it

Requires Node.js 18+ and Python 3 with `numpy` (the repository's `requirements.txt` is enough).

```bash
cd video
npm install
npm run music     # writes public/music.wav (a few seconds)
npm run dev       # Remotion Studio, with live preview
npm run render    # writes out/inditex_valuation.mp4
```

The first render downloads a headless Chrome (about 120 MB). To refresh the figures after changing the model, run `npm run data` (it needs the repository's processed data and runs the DCF and the Monte Carlo again).

## How the music stays in sync

Every scene and transition lasts a multiple of 15 frames, which is one beat at 120 BPM, so the cuts fall on the beat. The sound effects (hits, bells, pops) sit at the exact frames where the animations happen, listed in the `EV` table of `scripts/make_music.py`. If you change a scene's timing in `src/`, update that table and run `npm run music` again.

## License

The code is released under the MIT License of this repository. Remotion has its own license: it is free for individuals and teams of up to three people (see <https://www.remotion.pro/license>).
