import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { pop, prog } from "../anim";
import { C } from "../theme";
import { Beat, Check, Glass, Pop, Shell, Words, eur } from "../ui";
import data from "../data/modelData.json";

/* Beat A: la tasa de descuento se construye como una ecuación */
const WaccEquation: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const resP = pop(frame, fps, 45, { damping: 9, stiffness: 140 });
  return (
    <div style={{ marginTop: 34 }}>
      <Pop delay={0}>
        <div style={{ fontSize: 44, fontWeight: 700, color: C.muted }}>Discount rate = cost of equity</div>
      </Pop>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 28 }}>
        <Pop delay={15} from="left" style={{ flex: "none" }}>
          <Glass style={{ padding: "26px 26px", width: 330 }}>
            <div style={{ fontSize: 34, fontWeight: 700, color: C.muted }}>10-yr Bund</div>
            <div style={{ fontSize: 76, fontWeight: 900, color: C.green, whiteSpace: "nowrap" }}>3.57%</div>
          </Glass>
        </Pop>
        <Pop delay={22} from="scale" style={{ flex: "none" }}>
          <div style={{ fontSize: 72, fontWeight: 900, color: C.ink }}>+</div>
        </Pop>
        <Pop delay={30} from="right" style={{ flex: 1 }}>
          <Glass style={{ padding: "26px 24px" }}>
            <div style={{ fontSize: 34, fontWeight: 700, color: C.muted, whiteSpace: "nowrap" }}>Beta × risk premium</div>
            <div style={{ fontSize: 72, fontWeight: 900, color: C.amber, whiteSpace: "nowrap" }}>1.0 × 5.4%</div>
          </Glass>
        </Pop>
      </div>
      <div
        style={{
          marginTop: 34,
          display: "flex",
          alignItems: "baseline",
          gap: 26,
          opacity: Math.min(1, resP),
          transform: `scale(${0.6 + 0.4 * Math.min(resP, 1.15)})`,
          transformOrigin: "left center",
        }}
      >
        <span style={{ fontSize: 120, fontWeight: 900, color: C.ink }}>=</span>
        <span
          style={{
            fontSize: 220,
            fontWeight: 900,
            color: C.cyan,
            textShadow: "0 0 70px rgba(110,231,249,0.6)",
            lineHeight: 1,
          }}
        >
          8.97%
        </span>
      </div>
    </div>
  );
};

/* Beat B: tres escenarios + la réplica en Python */
const Scenarios: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items = [
    { k: "LOW", v: data.escenarios.low.valor, color: C.blue, delay: 0 },
    { k: "BASE", v: data.escenarios.base.valor, color: C.cyan, delay: 15 },
    { k: "HIGH", v: data.escenarios.high.valor, color: C.green, delay: 30 },
  ];
  return (
    <div style={{ marginTop: 30 }}>
      <Pop delay={0}>
        <div style={{ fontSize: 44, fontWeight: 700, color: C.muted }}>Value per share · 3 scenarios</div>
      </Pop>
      <div style={{ display: "flex", gap: 36, alignItems: "flex-end", marginTop: 22, height: 520 }}>
        {items.map((it) => {
          const p = pop(frame, fps, it.delay, { damping: 14, stiffness: 120, mass: 1 });
          const count = it.v * prog(frame, it.delay, 26);
          return (
            <div key={it.k} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end" }}>
              <div style={{ fontSize: 76, fontWeight: 900, color: it.color, fontVariantNumeric: "tabular-nums", marginBottom: 8, whiteSpace: "nowrap" }}>
                {eur(count, 1)}
              </div>
              <div
                style={{
                  width: "100%",
                  height: Math.max(0, it.v * 9 * Math.min(p, 1.05)),
                  borderRadius: "24px 24px 8px 8px",
                  background: `linear-gradient(180deg, ${it.color}, rgba(30,60,160,0.35))`,
                  boxShadow: `0 0 50px ${it.color}55`,
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "center",
                  paddingTop: 20,
                  fontSize: 44,
                  fontWeight: 900,
                  color: "#04102A",
                  letterSpacing: 3,
                }}
              >
                {it.k}
              </div>
            </div>
          );
        })}
      </div>
      <Pop delay={45} from="up" style={{ marginTop: 34 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20, fontSize: 44, fontWeight: 700 }}>
          <Check size={56} progress={prog(frame, 50, 10)} />
          <span>Python twin matches <span style={{ color: C.green }}>to the cent</span></span>
        </div>
      </Pop>
    </div>
  );
};

export const ExcelScene: React.FC = () => {
  return (
    <Shell tag="03 · Excel">
      <Words
        text="Excel builds the valuation"
        delay={4}
        stagger={5}
        highlight={{ from: 1, color: C.green }}
        style={{ marginTop: 44, fontSize: 92, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2 }}
      />
      <Pop delay={20} style={{ marginTop: 14 }}>
        <div style={{ fontSize: 42, fontWeight: 600, color: C.muted }}>10-year forecast · live formulas</div>
      </Pop>
      <div style={{ position: "relative", flex: 1 }}>
        <Beat from={0} to={105}>
          <WaccEquation />
        </Beat>
        <Beat from={105} to={225} fadeOut={false}>
          <Scenarios />
        </Beat>
      </div>
    </Shell>
  );
};
