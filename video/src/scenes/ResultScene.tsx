import React from "react";
import { useCurrentFrame } from "remotion";
import { prog } from "../anim";
import { C } from "../theme";
import { Pop, Shell, Words } from "../ui";
import data from "../data/modelData.json";

const PRICE = 54.38;
const MIN = 30;
const MAX = 66;
const W = 920;
const x = (v: number) => ((v - MIN) / (MAX - MIN)) * W;

type Row = { name: string; lo: number; hi: number; mark: number; color: string };

const ROWS: Row[] = [
  { name: "DCF · low to high", lo: data.escenarios.low.valor, hi: data.escenarios.high.valor, mark: data.escenarios.base.valor, color: C.blue },
  {
    name: "Peer multiples",
    lo: Math.min(data.comparables_mediana.per, data.comparables_mediana.ev_ebitda),
    hi: Math.max(data.comparables_mediana.per, data.comparables_mediana.ev_ebitda),
    mark: (data.comparables_mediana.per + data.comparables_mediana.ev_ebitda) / 2,
    color: C.cyan,
  },
  { name: "Monte Carlo · 90% of runs", lo: data.montecarlo.p5, hi: data.montecarlo.p95, mark: data.montecarlo.mediana, color: C.green },
  { name: "Analyst targets", lo: 41.5, hi: 65.0, mark: 59.54, color: C.red },
];

export const ResultScene: React.FC = () => {
  const frame = useCurrentFrame();
  const lineP = prog(frame, 60, 22);
  const rowH = 146;
  const top = 58;
  return (
    <Shell tag="05 · The result">
      <Words
        text="Four lenses, one gap"
        delay={4}
        stagger={5}
        highlight={{ from: 3, color: C.amber }}
        style={{ marginTop: 44, fontSize: 100, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2 }}
      />
      <div style={{ position: "relative", marginTop: 36, width: W, height: top + rowH * 4 + 60 }}>
        {ROWS.map((r, i) => {
          const p = prog(frame, 14 + i * 9, 22);
          return (
            <div key={r.name} style={{ position: "absolute", left: 0, top: top + i * rowH, width: W, opacity: Math.min(1, p * 2) }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                <span style={{ fontSize: 40, fontWeight: 800 }}>{r.name}</span>
                <span style={{ fontSize: 36, fontWeight: 600, color: C.muted, fontVariantNumeric: "tabular-nums" }}>
                  €{r.lo.toFixed(1)} – €{r.hi.toFixed(1)}
                </span>
              </div>
              <div style={{ position: "relative", height: 56, marginTop: 14 }}>
                <div style={{ position: "absolute", inset: 0, borderRadius: 28, backgroundColor: "rgba(255,255,255,0.06)" }} />
                <div
                  style={{
                    position: "absolute",
                    left: x(r.lo),
                    width: (x(r.hi) - x(r.lo)) * p,
                    height: 56,
                    borderRadius: 28,
                    backgroundColor: r.color,
                    boxShadow: `0 0 36px ${r.color}88`,
                  }}
                />
                <div
                  style={{
                    position: "absolute",
                    left: x(r.mark) - 4,
                    top: 7,
                    width: 8,
                    height: 42,
                    borderRadius: 4,
                    backgroundColor: "#fff",
                    opacity: p > 0.9 ? 1 : 0,
                  }}
                />
              </div>
            </div>
          );
        })}

        {/* Línea del precio de mercado */}
        <div
          style={{
            position: "absolute",
            left: x(PRICE) - 3,
            top: 40,
            width: 6,
            height: (rowH * 4 + 20) * lineP,
            borderRadius: 3,
            backgroundColor: C.amber,
            boxShadow: "0 0 30px rgba(255,181,71,0.9)",
          }}
        />
        <div style={{ position: "absolute", right: 0, top: -4, opacity: lineP }}>
          <div
            style={{
              fontSize: 36,
              fontWeight: 900,
              color: "#1A1000",
              backgroundColor: C.amber,
              padding: "6px 20px",
              borderRadius: 999,
              boxShadow: "0 0 30px rgba(255,181,71,0.6)",
            }}
          >
            price €{PRICE.toFixed(2)}
          </div>
        </div>

        {/* Eje */}
        <div style={{ position: "absolute", left: 0, top: top + rowH * 4 + 8, width: W, height: 40 }}>
          {[30, 40, 50, 60].map((t) => (
            <div key={t} style={{ position: "absolute", left: x(t), transform: t === 30 ? "none" : "translateX(-50%)", fontSize: 32, fontWeight: 600, color: C.muted }}>
              €{t}
            </div>
          ))}
        </div>
      </div>
      <Pop delay={96} style={{ marginTop: 10 }}>
        <div style={{ fontSize: 36, fontWeight: 600, color: C.muted }}>
          White tick = central estimate
        </div>
      </Pop>
    </Shell>
  );
};
