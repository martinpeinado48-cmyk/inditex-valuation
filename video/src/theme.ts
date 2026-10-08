import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

const inter = loadInter("normal", {
  weights: ["500", "600", "700", "800", "900"],
  subsets: ["latin", "greek"],
});
const mono = loadMono("normal", { weights: ["500", "700"], subsets: ["latin"] });

export const FONT = inter.fontFamily;
export const MONO = mono.fontFamily;

export const C = {
  ink: "#F4F7FF",
  muted: "#9FB0D6",
  blue: "#4C8DFF",
  cyan: "#6EE7F9",
  amber: "#FFB547",
  green: "#3DDC97",
  red: "#FF6B7A",
  panel: "linear-gradient(145deg, rgba(120,165,255,0.17), rgba(50,80,190,0.07))",
  panelBorder: "rgba(160,200,255,0.30)",
};

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1350;

// Duración de cada escena (frames a 30 fps) y de la transición entre escenas.
// Todo son múltiplos de 15 frames = 1 tiempo a 120 BPM, para que la música caiga en los cortes.
export const SCENE_FRAMES = {
  hook: 150,
  purpose: 150,
  data: 210,
  python: 240,
  excel: 225,
  stress: 330,
  result: 165,
  insight: 285,
  cta: 135,
} as const;

export const TRANSITION_FRAMES = 15;

const sceneSum = Object.values(SCENE_FRAMES).reduce((a, b) => a + b, 0);
export const TOTAL_FRAMES =
  sceneSum - (Object.keys(SCENE_FRAMES).length - 1) * TRANSITION_FRAMES;
