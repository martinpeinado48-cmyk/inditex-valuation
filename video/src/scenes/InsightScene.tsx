import React from "react";
import { useCurrentFrame } from "remotion";
import { prog } from "../anim";
import { C } from "../theme";
import { Beat, Glass, Pop, Shell, Words } from "../ui";

/* Beat A: la diferencia está en la tasa de descuento */
const Gap: React.FC = () => {
  const frame = useCurrentFrame();
  const sweep = prog(frame, 38, 30);
  const rate = 7.5 + (8.97 - 7.5) * sweep;
  return (
    <div>
      <Words
        text="The gap is the discount rate"
        delay={0}
        stagger={4}
        highlight={{ from: 3, color: C.cyan }}
        style={{ marginTop: 44, fontSize: 92, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2 }}
      />
      <div style={{ display: "flex", flexDirection: "column", gap: 64, marginTop: 100 }}>
        <Pop delay={14} from="left" distance={160}>
          <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
            <div style={{ width: 500, fontSize: 158, fontWeight: 900, color: C.amber, lineHeight: 1, textShadow: "0 0 50px rgba(255,181,71,0.4)" }}>
              ~7.5%
            </div>
            <div style={{ fontSize: 48, fontWeight: 700, lineHeight: 1.2 }}>
              implied by
              <br />
              today's price
            </div>
          </div>
        </Pop>
        <Pop delay={28} from="left" distance={160}>
          <div style={{ display: "flex", alignItems: "center", gap: 30 }}>
            <div style={{ width: 500, fontSize: 158, fontWeight: 900, color: C.cyan, lineHeight: 1, textShadow: "0 0 50px rgba(110,231,249,0.4)", fontVariantNumeric: "tabular-nums" }}>
              {rate.toFixed(2)}%
            </div>
            <div style={{ fontSize: 48, fontWeight: 700, lineHeight: 1.2 }}>
              my model's
              <br />
              discount rate
            </div>
          </div>
        </Pop>
      </div>
    </div>
  );
};

/* Beat B: gran negocio, la pregunta es el precio */
const Business: React.FC = () => {
  return (
    <div>
      <Words
        text="An excellent business"
        delay={0}
        stagger={5}
        highlight={{ from: 1, color: C.green }}
        style={{ marginTop: 44, fontSize: 100, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2 }}
      />
      <div style={{ display: "flex", flexDirection: "column", gap: 22, marginTop: 40 }}>
        <Pop delay={12} from="left" distance={160}>
          <Glass style={{ display: "flex", alignItems: "center", gap: 24, padding: "20px 36px" }} glow="rgba(61,220,151,0.22)">
            <span style={{ fontSize: 112, fontWeight: 900, color: C.green, width: 470, whiteSpace: "nowrap" }}>~40%</span>
            <span style={{ fontSize: 46, fontWeight: 700 }}>ROIC</span>
          </Glass>
        </Pop>
        <Pop delay={22} from="left" distance={160}>
          <Glass style={{ display: "flex", alignItems: "center", gap: 24, padding: "20px 36px" }} glow="rgba(61,220,151,0.22)">
            <span style={{ fontSize: 112, fontWeight: 900, color: C.green, width: 470, whiteSpace: "nowrap" }}>€10.4bn</span>
            <span style={{ fontSize: 46, fontWeight: 700, lineHeight: 1.15 }}>net cash</span>
          </Glass>
        </Pop>
      </div>
      <Pop delay={40} from="up" style={{ marginTop: 56 }}>
        <div style={{ fontSize: 68, fontWeight: 800, lineHeight: 1.18, letterSpacing: -1 }}>
          The question isn't quality.
          <br />
          It's the <span style={{ color: C.amber }}>price you pay</span> and the{" "}
          <span style={{ color: C.cyan }}>return you demand</span>.
        </div>
      </Pop>
    </div>
  );
};

export const InsightScene: React.FC = () => {
  return (
    <Shell tag="06 · The insight">
      <div style={{ position: "relative", flex: 1 }}>
        <Beat from={0} to={120}>
          <Gap />
        </Beat>
        <Beat from={120} to={285} fadeOut={false}>
          <Business />
        </Beat>
      </div>
    </Shell>
  );
};
