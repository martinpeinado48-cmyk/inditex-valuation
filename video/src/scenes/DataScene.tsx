import React from "react";
import { useCurrentFrame } from "remotion";
import { prog } from "../anim";
import { C } from "../theme";
import { Check, Glass, Pop, Shell, Words } from "../ui";

type Source = { badge: string; name: string; what: string; color: string };

const SOURCES: Source[] = [
  { badge: "PDF", name: "Inditex annual accounts", what: "Official PDFs · FY2020-25", color: C.amber },
  { badge: "$", name: "Yahoo Finance · Investing.com", what: "Prices · multiples · betas", color: C.cyan },
  { badge: "β", name: "Damodaran", what: "Risk premium · sector betas", color: C.blue },
  { badge: "%", name: "ECB · datosmacro", what: "Macro data · Bund yield", color: C.green },
  { badge: "24", name: "Bolsamanía · Bankinter", what: "Analyst consensus (24)", color: C.red },
];

const Row: React.FC<{ s: Source; index: number }> = ({ s, index }) => {
  const frame = useCurrentFrame();
  const delay = 30 + index * 15;
  const checkP = prog(frame, delay + 8, 10);
  return (
    <Pop delay={delay} from={index % 2 === 0 ? "left" : "right"} distance={220}>
      <Glass
        glow="rgba(70,130,255,0.18)"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 26,
          padding: "0 32px 0 28px",
          height: 116,
          borderRadius: 30,
        }}
      >
        <div
          style={{
            width: 78,
            height: 78,
            borderRadius: 22,
            flex: "none",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: s.badge.length > 2 ? 30 : 44,
            fontWeight: 900,
            color: s.color,
            border: `3px solid ${s.color}`,
            backgroundColor: "rgba(255,255,255,0.05)",
          }}
        >
          {s.badge}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 42, fontWeight: 800, lineHeight: 1.15 }}>{s.name}</div>
          <div style={{ fontSize: 33, fontWeight: 500, color: C.muted, marginTop: 4 }}>{s.what}</div>
        </div>
        <div style={{ opacity: checkP, scale: String(0.6 + 0.4 * checkP) }}>
          <Check size={52} progress={checkP} />
        </div>
      </Glass>
    </Pop>
  );
};

export const DataScene: React.FC = () => {
  return (
    <Shell tag="01 · The data">
      <Words
        text="Every number has a source"
        delay={4}
        stagger={5}
        highlight={{ from: 3, color: C.cyan }}
        style={{ marginTop: 36, fontSize: 90, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2 }}
      />
      <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 36 }}>
        {SOURCES.map((s, i) => (
          <Row key={s.name} s={s} index={i} />
        ))}
      </div>
      <Pop delay={105} style={{ marginTop: 28 }}>
        <div style={{ fontSize: 42, fontWeight: 600, color: C.ink, textAlign: "center", lineHeight: 1.25 }}>
          Every data point is saved with
          <br />
          its <span style={{ color: C.amber }}>source and date</span>
        </div>
      </Pop>
    </Shell>
  );
};
