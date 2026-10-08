import React from "react";
import { Sequence, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { prog } from "../anim";
import { C, MONO } from "../theme";
import { Arrow, Check, Glass, Pop, Shell, Words } from "../ui";
import data from "../data/modelData.json";

const FY = ["FY20", "FY21", "FY22", "FY23", "FY24", "FY25"];
const fmt = (n: number) => Math.round(n).toLocaleString("en-US");

/* Beat A: seis PDF entran en una tabla limpia (datos reales del proyecto) */
const PdfToTable: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 40 }}>
      {/* Pila de PDFs */}
      <div style={{ position: "relative", width: 236, height: 560, flex: "none" }}>
        {FY.map((label, i) => {
          const leave = prog(frame, 26 + i * 8, 14); // cada PDF "se va" hacia la tabla
          return (
            <Pop key={label} delay={i * 4} from="left" distance={100}>
              <div
                style={{
                  position: "absolute",
                  left: leave * 26,
                  top: 20 + i * 90,
                  width: 214,
                  height: 92,
                  borderRadius: 16,
                  border: `3px solid ${C.amber}`,
                  backgroundColor: "rgba(40,28,8,0.92)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "0 18px",
                  fontSize: 34,
                  fontWeight: 800,
                  opacity: 1 - 0.8 * leave,
                }}
              >
                <span style={{ color: C.amber }}>PDF</span>
                <span>{label}</span>
              </div>
            </Pop>
          );
        })}
      </div>

      <div style={{ flex: "none" }}>
        <Arrow size={60} />
      </div>

      {/* Tabla */}
      <Glass style={{ flex: 1, padding: "26px 26px", borderRadius: 28 }} glow="rgba(110,231,249,0.25)">
        <div style={{ fontFamily: MONO, fontSize: 27, color: C.cyan, fontWeight: 700, marginBottom: 14 }}>
          inditex_financials.csv
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "96px 1fr 1fr 1fr",
            fontSize: 30,
            fontWeight: 700,
            color: C.muted,
            paddingBottom: 8,
            borderBottom: `2px solid ${C.panelBorder}`,
          }}
        >
          <span>Year</span>
          <span style={{ textAlign: "right" }}>Sales</span>
          <span style={{ textAlign: "right" }}>EBIT</span>
          <span style={{ textAlign: "right" }}>Margin</span>
        </div>
        {data.historico.map((h, i) => {
          const p = prog(frame, 30 + i * 8, 10);
          return (
            <div
              key={h.year}
              style={{
                display: "grid",
                gridTemplateColumns: "96px 1fr 1fr 1fr",
                fontSize: 34,
                fontWeight: 600,
                height: 76,
                alignItems: "center",
                opacity: p,
                transform: `translateY(${(1 - p) * 20}px)`,
                fontVariantNumeric: "tabular-nums",
                borderBottom: "1px solid rgba(160,200,255,0.12)",
              }}
            >
              <span style={{ color: C.cyan }}>{FY[i]}</span>
              <span style={{ textAlign: "right" }}>{fmt(h.ventas)}</span>
              <span style={{ textAlign: "right" }}>{fmt(h.ebit)}</span>
              <span style={{ textAlign: "right", color: C.green }}>
                {((h.ebit / h.ventas) * 100).toFixed(1)}%
              </span>
            </div>
          );
        })}
        <div style={{ fontSize: 28, color: C.muted, marginTop: 12 }}>€ millions</div>
      </Glass>
    </div>
  );
};

/* Beat B: terminal con las comprobaciones contables */
const CHECKS = ["balance sheet balances", "EBITDA > EBIT > net income", "cash flow reconciles"];

const Terminal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const typed = (text: string, start: number) =>
    text.slice(0, Math.max(0, Math.floor((frame - start) * 2)));
  const cursorOn = Math.floor(frame / (fps / 3)) % 2 === 0;

  return (
    <div style={{ marginTop: 36 }}>
      <Pop delay={0} from="scale">
        <Glass
          style={{ padding: "40px 42px", backgroundColor: "rgba(2,6,20,0.7)" }}
          glow="rgba(61,220,151,0.22)"
        >
          <div style={{ display: "flex", gap: 12, marginBottom: 22 }}>
            {[C.red, C.amber, C.green].map((c) => (
              <div key={c} style={{ width: 20, height: 20, borderRadius: "50%", backgroundColor: c }} />
            ))}
          </div>
          <div style={{ fontFamily: MONO, fontSize: 40, fontWeight: 500, lineHeight: 1.8 }}>
            <div>
              <span style={{ color: C.cyan }}>$ </span>
              {typed("python extract_statements.py", 2)}
              {frame >= 2 && frame < 18 && cursorOn ? "▌" : ""}
            </div>
            <div>
              <span style={{ color: C.cyan }}>$ </span>
              {typed("python build_dataset.py", 18)}
              {frame >= 18 && frame < 30 && cursorOn ? "▌" : ""}
            </div>
            <div style={{ height: 14 }} />
            {CHECKS.map((c, i) => {
              const p = prog(frame, 30 + i * 15, 10);
              return (
                <div
                  key={c}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 18,
                    opacity: p,
                    transform: `translateX(${(1 - p) * -40}px)`,
                  }}
                >
                  <Check size={44} progress={p} />
                  <span style={{ color: C.green }}>{c}</span>
                </div>
              );
            })}
          </div>
        </Glass>
      </Pop>

      <Pop delay={75} from="up" style={{ marginTop: 34 }}>
        <div
          style={{
            display: "inline-block",
            fontSize: 42,
            fontWeight: 700,
            padding: "16px 36px",
            borderRadius: 999,
            border: `2px solid ${C.panelBorder}`,
            background: "rgba(90,140,255,0.16)",
          }}
        >
          Jupyter: margins · ROIC · cash flow
        </div>
      </Pop>
    </div>
  );
};

export const PythonScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const aOpacity = interpolate(frame, [108, 120], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <Shell tag="02 · Python">
      <Words
        text="Python turns PDFs into clean data"
        delay={4}
        stagger={4}
        highlight={{ from: 4, color: C.cyan }}
        style={{ marginTop: 44, fontSize: 88, fontWeight: 900, lineHeight: 1.06, letterSpacing: -2 }}
      />
      <div style={{ position: "relative", flex: 1 }}>
        <div style={{ position: "absolute", inset: 0, opacity: aOpacity }}>
          <PdfToTable />
        </div>
        <Sequence from={120} premountFor={fps}>
          <div style={{ position: "absolute", inset: 0 }}>
            <Terminal />
          </div>
        </Sequence>
      </div>
    </Shell>
  );
};
