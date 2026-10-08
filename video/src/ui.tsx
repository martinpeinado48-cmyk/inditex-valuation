import React, { useMemo } from "react";
import {
  AbsoluteFill,
  interpolate,
  random,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { pop } from "./anim";
import { C, FONT } from "./theme";

/* ---------- Fondo: degradado azul, brillos que se mueven y partículas ---------- */
export const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const t = frame / 30;

  const particles = useMemo(
    () =>
      Array.from({ length: 90 }, (_, i) => ({
        x: random(`px${i}`) * width,
        y0: random(`py${i}`) * height,
        speed: 8 + random(`ps${i}`) * 34,
        size: 2 + random(`pz${i}`) * 5,
        phase: random(`pf${i}`) * Math.PI * 2,
        rate: 0.6 + random(`pr${i}`) * 1.6,
      })),
    [width, height],
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#030612" }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(1000px 800px at ${50 + 10 * Math.sin(t * 0.5)}% ${
            28 + 5 * Math.cos(t * 0.4)
          }%, rgba(40,100,255,0.50), rgba(10,30,100,0) 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          background: `radial-gradient(900px 900px at ${25 + 12 * Math.cos(t * 0.35)}% ${
            88 + 4 * Math.sin(t * 0.5)
          }%, rgba(20,170,255,0.28), rgba(0,0,0,0) 65%)`,
        }}
      />
      {particles.map((p, i) => {
        const y = (((p.y0 - p.speed * t) % height) + height) % height;
        const alpha = 0.15 + 0.55 * Math.abs(Math.sin(t * p.rate + p.phase));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: p.x,
              top: y,
              width: p.size,
              height: p.size,
              borderRadius: "50%",
              backgroundColor: `rgba(170,205,255,${alpha})`,
              boxShadow: `0 0 ${p.size * 3}px rgba(120,170,255,${alpha})`,
            }}
          />
        );
      })}
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)",
        }}
      />
    </AbsoluteFill>
  );
};

/* ---------- Panel de cristal ---------- */
export const Glass: React.FC<{
  children?: React.ReactNode;
  style?: React.CSSProperties;
  glow?: string;
}> = ({ children, style, glow = "rgba(70,130,255,0.28)" }) => (
  <div
    style={{
      background: C.panel,
      border: `2px solid ${C.panelBorder}`,
      borderRadius: 36,
      boxShadow: `0 0 90px ${glow}, inset 0 2px 0 rgba(255,255,255,0.22)`,
      ...style,
    }}
  >
    {children}
  </div>
);

/* ---------- Entrada "pop" con rebote ---------- */
type From = "up" | "down" | "left" | "right" | "scale";
export const Pop: React.FC<{
  children: React.ReactNode;
  delay?: number;
  from?: From;
  style?: React.CSSProperties;
  distance?: number;
}> = ({ children, delay = 0, from = "up", style, distance = 60 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = pop(frame, fps, delay);
  const opacity = interpolate(p, [0, 0.35], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const off = (1 - p) * distance;
  const tx = from === "left" ? -off : from === "right" ? off : 0;
  const ty = from === "up" ? off : from === "down" ? -off : 0;
  const sc = from === "scale" ? 0.55 + 0.45 * p : 0.92 + 0.08 * p;
  return (
    <div
      style={{
        opacity,
        transform: `translate(${tx}px, ${ty}px) scale(${sc})`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/* ---------- Texto que entra palabra a palabra ---------- */
export const Words: React.FC<{
  text: string;
  delay?: number;
  stagger?: number;
  style?: React.CSSProperties;
  highlight?: { from: number; color: string };
}> = ({ text, delay = 0, stagger = 4, style, highlight }) => {
  const words = text.split(" ");
  return (
    <div style={{ display: "flex", flexWrap: "wrap", columnGap: "0.28em", ...style }}>
      {words.map((w, i) => (
        <Pop
          key={i}
          delay={delay + i * stagger}
          distance={40}
          style={{
            color: highlight && i >= highlight.from ? highlight.color : undefined,
          }}
        >
          {w}
        </Pop>
      ))}
    </div>
  );
};

/* ---------- Marco de escena con etiqueta de capítulo ---------- */
export const Shell: React.FC<{ tag: string; children: React.ReactNode }> = ({
  tag,
  children,
}) => (
  <AbsoluteFill
    style={{
      fontFamily: FONT,
      color: C.ink,
      padding: "100px 80px 110px",
      display: "flex",
      flexDirection: "column",
    }}
  >
    <Pop from="left" distance={80}>
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 16,
          padding: "12px 28px",
          borderRadius: 999,
          border: `2px solid ${C.panelBorder}`,
          background: "rgba(90,140,255,0.14)",
          fontSize: 34,
          fontWeight: 700,
          letterSpacing: 4,
          textTransform: "uppercase",
          color: C.cyan,
        }}
      >
        <span
          style={{
            width: 14,
            height: 14,
            borderRadius: "50%",
            backgroundColor: C.cyan,
            boxShadow: `0 0 18px ${C.cyan}`,
          }}
        />
        {tag}
      </div>
    </Pop>
    {children}
  </AbsoluteFill>
);

/* ---------- Iconos SVG sencillos ---------- */
export const Check: React.FC<{ size?: number; color?: string; progress?: number }> = ({
  size = 56,
  color = C.green,
  progress = 1,
}) => (
  <svg width={size} height={size} viewBox="0 0 56 56">
    <circle cx="28" cy="28" r="26" fill={color} fillOpacity={0.18} stroke={color} strokeWidth="3" />
    <path
      d="M16 29 L25 38 L41 19"
      fill="none"
      stroke={color}
      strokeWidth="5.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray={40}
      strokeDashoffset={40 * (1 - progress)}
    />
  </svg>
);

export const Arrow: React.FC<{ size?: number; color?: string; direction?: "right" | "down" }> = ({
  size = 64,
  color = C.cyan,
  direction = "right",
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 64 64"
    style={{ transform: direction === "down" ? "rotate(90deg)" : undefined }}
  >
    <path
      d="M10 32 H50 M36 17 L51 32 L36 47"
      fill="none"
      stroke={color}
      strokeWidth="6"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/* ---------- Sub-escena: ocupa todo el hueco y se desvanece al final ---------- */
const BeatInner: React.FC<{ dur: number; fadeOut: boolean; children: React.ReactNode }> = ({
  dur,
  fadeOut,
  children,
}) => {
  const f = useCurrentFrame();
  const o = fadeOut
    ? interpolate(f, [dur - 8, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 1;
  return <div style={{ position: "absolute", inset: 0, opacity: o }}>{children}</div>;
};

export const Beat: React.FC<{
  from: number;
  to: number;
  fadeOut?: boolean;
  children: React.ReactNode;
}> = ({ from, to, fadeOut = true, children }) => {
  const { fps } = useVideoConfig();
  return (
    <Sequence from={from} durationInFrames={to - from} premountFor={fps}>
      <BeatInner dur={to - from} fadeOut={fadeOut}>
        {children}
      </BeatInner>
    </Sequence>
  );
};

/** Formato de euros con dos decimales (punto decimal, como el post en inglés). */
export const eur = (v: number, d = 2): string => `€${v.toFixed(d)}`;
