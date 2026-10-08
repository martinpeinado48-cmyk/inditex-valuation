import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { C, MONO } from "../theme";
import { Glass, Pop, Shell, Words } from "../ui";

export const CtaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const glow = 0.5 + 0.5 * Math.sin(frame / 8);
  const spin = interpolate(frame, [0, 135], [-6, 6]);
  return (
    <Shell tag="Your turn">
      <Words
        text="What cost of capital would you use for Inditex?"
        delay={2}
        stagger={4}
        highlight={{ from: 3, color: C.cyan }}
        style={{ marginTop: 48, fontSize: 98, fontWeight: 900, lineHeight: 1.06, letterSpacing: -2 }}
      />
      <div style={{ perspective: 1800, marginTop: 54 }}>
        <div style={{ transform: `rotateX(4deg) rotateY(${spin}deg)` }}>
          <Pop delay={45} from="up" distance={120}>
            <Glass style={{ padding: "36px 44px" }} glow={`rgba(110,231,249,${0.2 + 0.2 * glow})`}>
              <div style={{ fontSize: 56, fontWeight: 900 }}>Martín Peinado Miraflores</div>
              <div style={{ fontSize: 38, fontWeight: 600, color: C.muted, marginTop: 6 }}>
                Business Administration · Complutense University of Madrid
              </div>
              <div style={{ height: 2, backgroundColor: C.panelBorder, margin: "26px 0" }} />
              <div style={{ fontFamily: MONO, fontSize: 36, fontWeight: 700, color: C.cyan, lineHeight: 1.45 }}>
                github.com/martinpeinado48-cmyk/
                <br />
                inditex-valuation
              </div>
              <div style={{ display: "flex", gap: 16, marginTop: 26, flexWrap: "wrap" }}>
                {["Excel", "Python", "MIT license"].map((t) => (
                  <div
                    key={t}
                    style={{
                      fontSize: 38,
                      fontWeight: 700,
                      padding: "10px 28px",
                      borderRadius: 999,
                      border: `2px solid ${C.panelBorder}`,
                      background: "rgba(90,140,255,0.16)",
                    }}
                  >
                    {t}
                  </div>
                ))}
              </div>
            </Glass>
          </Pop>
        </div>
      </div>
      <Pop delay={70} style={{ marginTop: 44 }}>
        <div style={{ fontSize: 34, fontWeight: 500, color: C.muted, lineHeight: 1.4 }}>
          Educational project · not investment advice
          <br />
          Built with Claude Code + Remotion
        </div>
      </Pop>
    </Shell>
  );
};
