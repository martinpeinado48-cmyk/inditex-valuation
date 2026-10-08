import { Easing, interpolate, spring } from "remotion";

export const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);

/** Progreso 0→1 con salida suave, empezando en `start` y durando `dur` frames. */
export const prog = (frame: number, start: number, dur: number): number =>
  interpolate(frame, [start, start + dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: EASE_OUT,
  });

/** Muelle con rebote para entradas "pop". */
export const pop = (
  frame: number,
  fps: number,
  delay: number,
  config: { damping?: number; stiffness?: number; mass?: number } = {},
): number =>
  spring({
    frame: frame - delay,
    fps,
    config: { damping: 13, stiffness: 170, mass: 0.7, ...config },
  });

/** Aparece (0→1) y desaparece (1→0) en una ventana de frames. */
export const window01 = (
  frame: number,
  inStart: number,
  inDur: number,
  outStart: number,
  outDur: number,
): number => prog(frame, inStart, inDur) * (1 - prog(frame, outStart, outDur));
