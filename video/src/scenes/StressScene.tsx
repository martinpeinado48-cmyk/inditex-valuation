import React from "react";
import { useCurrentFrame } from "remotion";
import { prog } from "../anim";
import { C } from "../theme";
import { Arrow, Beat, Check, Glass, Pop, Shell, Words } from "../ui";
import data from "../data/modelData.json";

/* Beat A: comparables, con los múltiplos reales de cada empresa */
const Peers: React.FC = () => {
  return (
    <div style={{ marginTop: 34 }}>
      <Pop delay={0}>
        <div style={{ fontSize: 44, fontWeight: 700, color: C.muted }}>Peer multiples</div>
      </Pop>
      <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 24 }}>
        {data.comparables.map((p, i) => (
          <Pop key={p.nombre} delay={6 + i * 8} from="left" distance={160}>
            <Glass
              style={{ padding: "0 34px", height: 108, borderRadius: 28, display: "flex", alignItems: "center", justifyContent: "space-between" }}
              glow="rgba(70,130,255,0.2)"
            >
              <span style={{ fontSize: 46, fontWeight: 800 }}>{p.nombre}</span>
              <span style={{ fontSize: 34, fontWeight: 600, color: C.muted, fontVariantNumeric: "tabular-nums" }}>
                P/E <span style={{ color: C.ink }}>{p.per.toFixed(1)}</span> · EV/EBITDA{" "}
                <span style={{ color: C.ink }}>{p.ev_ebitda.toFixed(1)}</span>
              </span>
            </Glass>
          </Pop>
        ))}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 24, marginTop: 30 }}>
        <Pop delay={28} from="scale" style={{ flex: "none" }}>
          <Arrow size={72} direction="down" />
        </Pop>
        <Pop delay={30} from="right" distance={140}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 24 }}>
            <span
              style={{
                fontSize: 132,
                fontWeight: 900,
                color: C.cyan,
                lineHeight: 1,
                textShadow: "0 0 60px rgba(110,231,249,0.5)",
                whiteSpace: "nowrap",
              }}
            >
              €42–45
            </span>
            <span style={{ fontSize: 44, fontWeight: 700, color: C.muted }}>per share</span>
          </div>
        </Pop>
      </div>
      <Pop delay={50} style={{ marginTop: 18 }}>
        <div style={{ fontSize: 40, fontWeight: 600, color: C.muted }}>Median of the three peers</div>
      </Pop>
    </div>
  );
};

/* Beat B: Monte Carlo con el histograma real de las 20.000 simulaciones */
const MonteCarlo: React.FC = () => {
  const frame = useCurrentFrame();
  const mc = data.montecarlo;
  const BINS = 48; // 20 € → 80 €
  const counts = mc.counts.slice(0, BINS);
  const max = Math.max(...counts);
  const W = 860;
  const H = 330;
  const bw = W / BINS;
  const priceX = ((mc.precio - mc.bin_lo) / 60) * W;
  const sims = Math.round(mc.n * prog(frame, 4, 42));
  const lineP = prog(frame, 45, 14);
  const pctP = prog(frame, 54, 18);

  return (
    <div style={{ marginTop: 30 }}>
      <Pop delay={0}>
        <div style={{ fontSize: 44, fontWeight: 700, color: C.muted, fontVariantNumeric: "tabular-nums" }}>
          Monte Carlo · <span style={{ color: C.ink }}>{sims.toLocaleString("en-US")}</span> simulations
        </div>
      </Pop>
      <Glass style={{ marginTop: 20, padding: "46px 30px 20px" }} glow="rgba(70,130,255,0.25)">
        <div style={{ position: "relative", width: W, height: H }}>
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "flex-end" }}>
            {counts.map((c, i) => {
              const centre = mc.bin_lo + (i + 0.5) * 1.25;
              const above = centre >= mc.precio;
              const p = prog(frame, 4 + i * 0.7, 14);
              return (
                <div
                  key={i}
                  style={{
                    width: bw - 3,
                    marginRight: 3,
                    height: (c / max) * H * p,
                    borderRadius: "5px 5px 0 0",
                    backgroundColor: above ? C.amber : C.blue,
                    boxShadow: above ? "0 0 18px rgba(255,181,71,0.55)" : "none",
                  }}
                />
              );
            })}
          </div>
          <div
            style={{
              position: "absolute",
              left: priceX - 2,
              top: -36,
              width: 4,
              height: (H + 36) * lineP,
              backgroundColor: C.amber,
              borderRadius: 2,
              opacity: lineP,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: priceX + 12,
              top: -46,
              fontSize: 34,
              fontWeight: 800,
              color: C.amber,
              opacity: lineP,
              whiteSpace: "nowrap",
            }}
          >
            price €{mc.precio.toFixed(2)}
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 32, fontWeight: 600, color: C.muted, marginTop: 10 }}>
          <span>€20</span>
          <span>€50</span>
          <span>€80</span>
        </div>
      </Glass>
      <div
        style={{
          marginTop: 26,
          display: "flex",
          alignItems: "center",
          gap: 28,
          opacity: pctP,
          transform: `translateY(${(1 - pctP) * 40}px)`,
        }}
      >
        <div style={{ fontSize: 150, fontWeight: 900, color: C.amber, lineHeight: 1, textShadow: "0 0 50px rgba(255,181,71,0.45)" }}>
          {(mc.prob_supera * 100).toFixed(1)}%
        </div>
        <div style={{ fontSize: 44, fontWeight: 700, lineHeight: 1.2 }}>
          of runs value it
          <br />
          above today's price
        </div>
      </div>
    </div>
  );
};

/* Beat C: calidad contable (Altman y Beneish) */
const Gauge: React.FC<{
  title: string;
  range: string;
  lo: number;
  hi: number;
  min: number;
  max: number;
  threshold: number;
  thresholdLabel: string;
  dangerSide: "left" | "right";
  delay: number;
}> = ({ title, range, lo, hi, min, max, threshold, thresholdLabel, dangerSide, delay }) => {
  const frame = useCurrentFrame();
  const W = 840;
  const x = (v: number) => ((v - min) / (max - min)) * W;
  const grow = prog(frame, delay + 8, 20);
  const safeStart = dangerSide === "right" ? 0 : x(threshold);
  const safeWidth = dangerSide === "right" ? x(threshold) : W - x(threshold);
  return (
    <Pop delay={delay} from="left" distance={160}>
      <Glass style={{ padding: "26px 40px 24px", borderRadius: 30 }} glow="rgba(61,220,151,0.18)">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <div style={{ fontSize: 42, fontWeight: 800 }}>{title}</div>
          <div style={{ fontSize: 58, fontWeight: 900, color: C.green, fontVariantNumeric: "tabular-nums" }}>{range}</div>
        </div>
        <div style={{ position: "relative", width: W, height: 28, marginTop: 20, borderRadius: 14, backgroundColor: "rgba(255,255,255,0.08)" }}>
          <div
            style={{
              position: "absolute",
              left: safeStart,
              width: safeWidth,
              height: 28,
              borderRadius: 14,
              backgroundColor: "rgba(61,220,151,0.12)",
            }}
          />
          <div
            style={{
              position: "absolute",
              left: x(lo),
              width: (x(hi) - x(lo)) * grow,
              height: 28,
              borderRadius: 14,
              backgroundColor: C.green,
              boxShadow: "0 0 30px rgba(61,220,151,0.7)",
            }}
          />
          <div style={{ position: "absolute", left: x(threshold) - 2, top: -8, width: 4, height: 44, backgroundColor: C.amber, borderRadius: 2 }} />
        </div>
        <div
          style={{
            marginTop: 12,
            fontSize: 34,
            fontWeight: 600,
            color: C.muted,
            marginLeft: Math.max(0, x(threshold) - 150),
            whiteSpace: "nowrap",
          }}
        >
          {thresholdLabel}
        </div>
      </Glass>
    </Pop>
  );
};

const Quality: React.FC = () => {
  const frame = useCurrentFrame();
  const a = data.altman;
  const b = data.beneish;
  const fin = prog(frame, 45, 12);
  return (
    <div style={{ marginTop: 30, display: "flex", flexDirection: "column", gap: 22 }}>
      <Pop delay={0}>
        <div style={{ fontSize: 44, fontWeight: 700, color: C.muted }}>Accounting-quality screens</div>
      </Pop>
      <Gauge
        title="Altman Z″"
        range={`${a.min.toFixed(1)}–${a.max.toFixed(1)}`}
        lo={a.min}
        hi={a.max}
        min={0}
        max={7}
        threshold={2.6}
        thresholdLabel="safe above 2.6"
        dangerSide="left"
        delay={6}
      />
      <Gauge
        title="Beneish M"
        range={`${b.max.toFixed(2)} to ${b.min.toFixed(2)}`.replace(/-/g, "−")}
        lo={b.min}
        hi={b.max}
        min={-3.5}
        max={-1}
        threshold={-1.78}
        thresholdLabel="alert above −1.78"
        dangerSide="right"
        delay={22}
      />
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 24,
          marginTop: 6,
          opacity: fin,
          transform: `scale(${0.7 + 0.3 * fin})`,
          transformOrigin: "left center",
        }}
      >
        <Check size={84} progress={fin} />
        <div style={{ fontSize: 64, fontWeight: 900, color: C.green }}>No red flags</div>
      </div>
    </div>
  );
};

export const StressScene: React.FC = () => {
  return (
    <Shell tag="04 · Stress test">
      <Words
        text="Then I tried to break it"
        delay={4}
        stagger={5}
        highlight={{ from: 3, color: C.red }}
        style={{ marginTop: 44, fontSize: 96, fontWeight: 900, lineHeight: 1.05, letterSpacing: -2 }}
      />
      <div style={{ position: "relative", flex: 1 }}>
        <Beat from={0} to={105}>
          <Peers />
        </Beat>
        <Beat from={105} to={225}>
          <MonteCarlo />
        </Beat>
        <Beat from={225} to={330} fadeOut={false}>
          <Quality />
        </Beat>
      </div>
    </Shell>
  );
};
