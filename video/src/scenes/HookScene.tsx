import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { prog } from "../anim";
import { C } from "../theme";
import { Glass, Pop, Shell, Words, eur } from "../ui";

const PRICE = 54.38;
const MODEL = 42.87;

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();

  // Cámara 3D que se mueve despacio durante toda la escena
  const rotX = interpolate(frame, [0, 150], [9, 3]);
  const rotY = interpolate(frame, [0, 150], [-9, 5]);

  // Sacudida cuando aparece el valor del modelo
  const shake = frame >= 30 && frame < 46 ? Math.sin(frame * 4.2) * interpolate(frame, [30, 46], [16, 0]) : 0;

  const priceShown = PRICE * prog(frame, 4, 22);
  const modelShown = MODEL * prog(frame, 34, 22);

  return (
    <Shell tag="The question">
      <div style={{ perspective: 1800, marginTop: 56 }}>
        <div
          style={{
            position: "relative",
            transformStyle: "preserve-3d",
            transform: `rotateX(${rotX}deg) rotateY(${rotY}deg)`,
          }}
        >
          <Pop delay={0} from="left" distance={160}>
            <Glass
              style={{ padding: "34px 50px", height: 292 }}
              glow="rgba(255,181,71,0.30)"
            >
              <div style={{ fontSize: 38, fontWeight: 700, color: C.muted, letterSpacing: 2 }}>
                MARKET PRICE · 7 OCT 2026
              </div>
              <div
                style={{
                  fontSize: 196,
                  fontWeight: 900,
                  lineHeight: 1.05,
                  color: C.amber,
                  fontVariantNumeric: "tabular-nums",
                  textShadow: "0 0 50px rgba(255,181,71,0.45)",
                }}
              >
                {eur(priceShown)}
              </div>
            </Glass>
          </Pop>

          <div style={{ height: 44 }} />

          <div style={{ transform: `translateX(${shake}px)` }}>
            <Pop delay={30} from="right" distance={160}>
              <Glass
                style={{ padding: "34px 50px", height: 292 }}
                glow="rgba(110,231,249,0.32)"
              >
                <div style={{ fontSize: 38, fontWeight: 700, color: C.muted, letterSpacing: 2 }}>
                  MY MODEL (DCF)
                </div>
                <div
                  style={{
                    fontSize: 196,
                    fontWeight: 900,
                    lineHeight: 1.05,
                    color: C.cyan,
                    fontVariantNumeric: "tabular-nums",
                    textShadow: "0 0 50px rgba(110,231,249,0.45)",
                  }}
                >
                  {eur(modelShown)}
                </div>
              </Glass>
            </Pop>
          </div>

          <div style={{ position: "absolute", right: 34, top: 258 }}>
            <Pop delay={60} from="scale">
              <div
                style={{
                  padding: "14px 36px",
                  borderRadius: 999,
                  backgroundColor: C.red,
                  color: "#1A0408",
                  fontSize: 64,
                  fontWeight: 900,
                  boxShadow: "0 0 50px rgba(255,107,122,0.6)",
                }}
              >
                −21%
              </div>
            </Pop>
          </div>
        </div>
      </div>

      <Words
        text="Is the market wrong… or am I?"
        delay={72}
        stagger={4}
        highlight={{ from: 4, color: C.amber }}
        style={{
          marginTop: 92,
          fontSize: 104,
          fontWeight: 900,
          lineHeight: 1.08,
          letterSpacing: -2,
        }}
      />
    </Shell>
  );
};
