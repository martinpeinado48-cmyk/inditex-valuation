import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C } from "../theme";
import { Pop, Shell, Words } from "../ui";

const CHIPS = ["Corporate finance", "Excel + Python", "100% open source"];

export const PurposeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const spin = interpolate(frame, [0, 150], [-35, 35]);

  return (
    <Shell tag="The goal">
      {/* Signo de interrogación gigante girando en 3D al fondo */}
      <div
        style={{
          position: "absolute",
          right: -40,
          top: 160,
          perspective: 1400,
          opacity: 0.16,
        }}
      >
        <div
          style={{
            fontSize: 1150,
            fontWeight: 900,
            lineHeight: 1,
            color: C.blue,
            transform: `rotateY(${spin}deg)`,
          }}
        >
          ?
        </div>
      </div>

      <div style={{ marginTop: 64 }}>
        <Words
          text="What is a company really worth?"
          delay={4}
          stagger={5}
          highlight={{ from: 4, color: C.cyan }}
          style={{ fontSize: 114, fontWeight: 900, lineHeight: 1.06, letterSpacing: -3 }}
        />
      </div>

      <Pop delay={30} style={{ marginTop: 44 }}>
        <div style={{ fontSize: 52, fontWeight: 600, lineHeight: 1.3, color: C.ink, maxWidth: 900 }}>
          A personal project: from{" "}
          <span style={{ color: C.cyan }}>raw PDFs</span> to a number I can{" "}
          <span style={{ color: C.amber }}>defend</span>.
        </div>
      </Pop>

      <div style={{ display: "flex", flexDirection: "column", gap: 18, marginTop: 44, alignItems: "flex-start" }}>
        {CHIPS.map((c, i) => (
          <Pop key={c} delay={60 + i * 15} from="left" distance={120}>
            <div
              style={{
                fontSize: 48,
                fontWeight: 700,
                padding: "16px 40px",
                borderRadius: 999,
                border: `2px solid ${C.panelBorder}`,
                background: "rgba(90,140,255,0.16)",
              }}
            >
              {c}
            </div>
          </Pop>
        ))}
      </div>
    </Shell>
  );
};
