"""Compone la música y los efectos del vídeo de Inditex (original, sintetizada con numpy; sin derechos de terceros).

120 BPM, La menor, progresión Am - F - C - G (un acorde por compás). Todas las escenas y transiciones del vídeo duran un
múltiplo de 15 frames (= 1 tiempo a 30 fps), así que los cortes caen en los tiempos de la música.

Los efectos de sonido (golpes, acordes de campana, "pops") están colocados en los frames exactos de la animación: si se
cambian los tiempos de las escenas en src/theme.ts o src/scenes/*.tsx, hay que actualizar EVENTOS aquí abajo.

Uso:  python scripts/make_music.py public/music.wav [--plot informe_mezcla.png]
"""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100
FPS = 30
BPM = 120
BEAT = 60.0 / BPM  # 0,5 s = 15 frames

# ---- Estructura del vídeo (igual que src/theme.ts) -------------------------------------------------------------------
SCENES = dict(hook=150, purpose=150, data=210, python=240, excel=225, stress=330, result=165, insight=285, cta=135)
TR = 15
START = {}
_t = 0
for _k, _v in SCENES.items():
    START[_k] = _t
    _t += _v - TR
TOTAL_FRAMES = _t + TR
N = int(round(TOTAL_FRAMES / FPS * SR))
TOTAL_BEATS = TOTAL_FRAMES / 15

rng = np.random.default_rng(2026)


def f2s(frame):
    return int(round(frame / FPS * SR))


def b2s(beat):
    return int(round(beat * BEAT * SR))


def b2f(beat):
    return beat * 15


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---- Filtros (zero-phase, por FFT) ------------------------------------------------------------------------------------
def _nfft(n):
    return 1 << int(np.ceil(np.log2(max(n, 2))))


def lp(x, fc, order=2):
    nf = _nfft(len(x))
    X = np.fft.rfft(x, nf)
    f = np.fft.rfftfreq(nf, 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** (2 * order))
    return np.fft.irfft(X, nf)[: len(x)]


def hp(x, fc, order=2):
    nf = _nfft(len(x))
    X = np.fft.rfft(x, nf)
    f = np.fft.rfftfreq(nf, 1 / SR)
    r = (f / fc) ** (2 * order)
    X *= np.sqrt(r / (1 + r))
    return np.fft.irfft(X, nf)[: len(x)]


def lp_sweep(x, f0, f1, passes=2):
    """Paso bajo de un polo cuyo corte barre de f0 a f1 (exponencial) a lo largo de la señal."""
    n = len(x)
    fc = f0 * (f1 / f0) ** (np.arange(n) / max(n - 1, 1))
    a = 1 - np.exp(-2 * np.pi * fc / SR)
    y = x
    for _ in range(passes):
        out = np.empty(n)
        s = 0.0
        for i in range(n):
            s += a[i] * (y[i] - s)
            out[i] = s
        y = out
    return y


def fftconv(x, ir):
    nfft = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[: len(x)]


# ---- Buses estéreo ----------------------------------------------------------------------------------------------------
class Bus:
    def __init__(self):
        self.l = np.zeros(N)
        self.r = np.zeros(N)

    def add(self, sig, start, gain=1.0, pan=0.0):
        """sig: array mono o tupla (l, r). pan -1..1 (reparto de igual potencia)."""
        if start >= N:
            return
        if isinstance(sig, tuple):
            sl, sr_ = sig
            gl = gr = gain
        else:
            sl = sr_ = sig
            ang = (pan + 1) * np.pi / 4
            gl, gr = gain * np.cos(ang) * np.sqrt(2), gain * np.sin(ang) * np.sqrt(2)
        n = min(len(sl), N - start)
        if n <= 0:
            return
        self.l[start:start + n] += sl[:n] * gl
        self.r[start:start + n] += sr_[:n] * gr


def tt(dur):
    return np.arange(int(dur * SR)) / SR


# ---- Sintetizadores ---------------------------------------------------------------------------------------------------
def saw_add(f, t, K=14, rolloff=1.6, phase=0.0):
    """Diente de sierra por suma aditiva, con filtrado suave de agudos; sin aliasing."""
    y = np.zeros_like(t)
    for k in range(1, int(min(K, SR * 0.45 / f)) + 1):
        y += np.sin(2 * np.pi * k * f * t + phase * k) / k ** rolloff
    return y


def pad_chord(midis, dur=2.0, rel=0.9):
    """Pad cálido estéreo: 3 sierras desafinadas por nota, ataque lento."""
    t = tt(dur + rel)
    env = np.minimum(1, 1 - np.exp(-t / 0.18))
    tail = t > dur
    env[tail] *= np.exp(-(t[tail] - dur) / (rel / 3.2))
    l = np.zeros_like(t)
    r = np.zeros_like(t)
    for m in midis:
        f = midi_hz(m)
        for cents, ph, side in ((-9, 0.3, "l"), (0, 1.1, "m"), (9, 2.2, "r")):
            y = saw_add(f * 2 ** (cents / 1200), t, K=12, rolloff=1.9, phase=ph)
            if side in ("l", "m"):
                l += y * (0.7 if side == "m" else 1.0)
            if side in ("r", "m"):
                r += y * (0.7 if side == "m" else 1.0)
    return l * env, r * env


def bass_note(m, dur=0.42):
    t = tt(dur)
    f = midi_hz(m)
    env = np.minimum(1, t / 0.006) * np.exp(-t * 4.5)
    sub = np.sin(2 * np.pi * f * t)
    mid = saw_add(f * 2, t, K=8, rolloff=1.5)  # octava superior, audible en altavoces de móvil
    return (sub * 0.9 + lp(mid, 700, 2) * 0.55) * env


def pluck(m, dur=0.5):
    t = tt(dur)
    f = midi_hz(m)
    y = np.zeros_like(t)
    for k, a in ((1, 1.0), (2, 0.6), (3, 0.45), (4, 0.32), (6, 0.18), (8, 0.09)):
        if k * f < 10000:
            y += a * np.sin(2 * np.pi * k * f * t) * np.exp(-t * (4 + 3.5 * k))
    return y * np.minimum(1, t / 0.002)


def bell(f, dur=1.6, bright=1.0):
    t = tt(dur)
    y = np.zeros_like(t)
    for ratio, a, d in ((1.0, 1.0, 2.6), (2.76, 0.4 * bright, 4.2), (5.40, 0.2 * bright, 6.5), (8.93, 0.08 * bright, 9.0)):
        y += a * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * d)
    return y * np.minimum(1, t / 0.002)


def kick():
    t = tt(0.5)
    f = 46 + 110 * np.exp(-t * 38)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t * 8.5)
    click = rng.standard_normal(len(t)) * np.exp(-t * 900) * 0.25
    return np.tanh((y + click) * 1.3)


def hat(open_=False):
    d = 0.28 if open_ else 0.06
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 7500, 2) * np.exp(-t * (16 if open_ else 80))


def clap():
    t = tt(0.32)
    n = rng.standard_normal(len(t))
    env = np.exp(-t * 20) * 0.7
    for i, off in enumerate((0.0, 0.011, 0.022)):
        k = int(off * SR)
        env[k:] += np.exp(-(t[: len(t) - k]) * 260) * (1.0 - 0.15 * i)
    return hp(lp(n, 5200, 2), 900, 2) * env


def tick(f=2400, dur=0.025):
    t = tt(dur)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 260) * np.minimum(1, t / 0.0006)


def key_click():
    t = tt(0.02)
    return hp(rng.standard_normal(len(t)), 2500, 2) * np.exp(-t * 330)


def pop_snd(f0=820):
    t = tt(0.14)
    f = 260 + (f0 - 260) * np.exp(-t * 22)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 26) * np.minimum(1, t / 0.001)


def impact(dur=2.4, depth=1.0):
    t = tt(dur)
    f = 30 + 70 * np.exp(-t * 7)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.0)
    noise = lp(rng.standard_normal(len(t)), 900, 2) * np.exp(-t * 5.5) * 0.6
    boom = lp(rng.standard_normal(len(t)), 220, 2) * np.exp(-t * 3.0) * 0.5
    return (sub * depth + noise + boom) * np.minimum(1, t / 0.002)


def whoosh(dur=0.5):
    n = rng.standard_normal(int(dur * SR))
    y = lp_sweep(n, 300, 7000, passes=2)
    t = np.linspace(0, 1, len(y))
    return y * np.sin(np.pi * t) ** 1.5


def riser(dur, f_end=1900):
    k = int(dur * SR)
    t = np.linspace(0, 1, k)
    n = lp_sweep(rng.standard_normal(k), 250, 9000, passes=2)
    tone_f = 180 * (f_end / 180) ** t
    tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR)
    env = t ** 2.2
    return (n * 0.9 + tone * 0.25) * env


def glide(f0, f1, dur):
    t = np.linspace(0, 1, int(dur * SR))
    f = f0 * (f1 / f0) ** t
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t) ** 1.2


def make_ir(rt60=2.1, seed=5):
    n = int(rt60 * 1.25 * SR)
    t = np.arange(n) / SR
    irs = []
    for s in (seed, seed + 1):
        r = np.random.default_rng(s).standard_normal(n) * np.exp(-6.91 * t / rt60)
        r = lp(r, 6500, 1)
        r = np.concatenate([np.zeros(int(0.012 * SR)), r])
        irs.append(r / np.sqrt(np.sum(r ** 2)))
    return irs


# ---- Armonía ------------------------------------------------------------------------------------------------------------
# Am - F - C - G con conducción de voces suave
PAD_VOICING = [[57, 60, 64], [57, 60, 65], [55, 60, 64], [55, 59, 62]]
BASS_ROOT = [33, 29, 36, 31]     # A1 F1 C2 G1
ARP_TONES = [[57, 60, 64, 69], [57, 60, 65, 69], [55, 60, 64, 67], [55, 59, 62, 67]]
ARP_P8 = [0, 1, 2, 3, 2, 3, 1, 2]


def chord_of_bar(bar):
    return 0 if bar >= 28 else bar % 4  # el final se queda en La menor (resuelve)


# ---- Arreglo (en tiempos) -------------------------------------------------------------------------------------------
def span(b, spans):
    return any(a <= b < z for a, z in spans)


GROOVE = [(10, 91), (99, 112.5)]
ARP_SPANS = [(19, 116)]
HAT_SPANS = [(19, 91), (99, 112.5)]
HAT16_SPANS = [(60, 91), (99, 112.5)]
CLAP_SPANS = [(31, 91), (99, 112.5)]


def G(points, b):
    return float(np.interp(b, [p[0] for p in points], [p[1] for p in points]))


KICK_G = [(10, 0.7), (19, 0.85), (60, 0.95), (81, 1.0), (99, 1.0), (112, 0.9)]
BASS_G = [(10, 0.7), (46, 0.8), (60, 0.95), (99, 0.95), (112, 0.8)]
PAD_G = [(0, 0.0), (3, 0.5), (10, 0.55), (46, 0.6), (60, 0.65), (81, 0.7), (90.5, 0.7), (92, 0.95), (98.5, 0.95),
         (100, 0.65), (112, 0.8), (118, 0.8)]
ARP_G = [(19, 0.0), (21, 0.55), (46, 0.62), (60, 0.72), (90, 0.72), (91, 0.55), (98, 0.6), (99, 0.7), (112, 0.5), (116, 0.0)]
HAT_G = [(19, 0.5), (60, 0.65), (99, 0.7)]
CLAP_G = [(31, 0.4), (46, 0.5), (60, 0.65), (81, 0.7), (99, 0.7)]


def arp_mode(b):
    """Devuelve (paso en tiempos, octava extra)."""
    if 19 <= b < 46:
        return 0.5, 0
    if 46 <= b < 91:
        return 0.25, 0
    if 91 <= b < 99:
        return 0.5, 12
    if 99 <= b < 112:
        return 0.25, 0
    return 0.5, 0


# ---- Efectos sincronizados con la animación -----------------------------------------------------------------------
def S(scene, local):
    return START[scene] + local


# frames globales exactos de cada evento visual (ver los delays de cada escena)
EV = dict(
    hit_big=[30, 60],
    hook_count_price=list(range(4, 27, 3)),
    hook_count_model=list(range(34, 57, 3)),
    drop_riser=(62, 150),
    purpose_chips=[S("purpose", 60), S("purpose", 75), S("purpose", 90)],
    data_rows=[S("data", 30 + 15 * i) for i in range(5)],
    py_rows=[S("python", 30 + 8 * i) for i in range(6)],
    py_type1=list(range(S("python", 120 + 2), S("python", 120 + 17), 3)),
    py_type2=list(range(S("python", 120 + 18), S("python", 120 + 30), 3)),
    py_checks=[S("python", 120 + 30), S("python", 120 + 45), S("python", 120 + 60)],
    py_chip=S("python", 120 + 75),
    excel_cards=[S("excel", 15), S("excel", 30)],
    excel_plus=S("excel", 22),
    excel_result=S("excel", 45),
    excel_bars=[S("excel", 105 + 0), S("excel", 105 + 15), S("excel", 105 + 30)],
    excel_check=S("excel", 105 + 45),
    peers_rows=[S("stress", 6), S("stress", 14), S("stress", 22)],
    peers_result=S("stress", 30),
    mc_count=list(range(S("stress", 105 + 4), S("stress", 105 + 46), 3)),
    mc_riser=(S("stress", 105 + 4), S("stress", 105 + 45)),
    mc_hit=S("stress", 105 + 45),
    mc_pct=S("stress", 105 + 54),
    q_gauges=[S("stress", 225 + 6), S("stress", 225 + 22)],
    q_check=S("stress", 225 + 45),
    res_rows=[S("result", 14 + 9 * i) for i in range(4)],
    res_line=S("result", 60),
    ins_pops=[S("insight", 14), S("insight", 28)],
    ins_glide=(S("insight", 38), S("insight", 68)),
    bus_riser=(S("insight", 68), S("insight", 120)),
    bus_drop=S("insight", 120),
    bus_pops=[S("insight", 120 + 12), S("insight", 120 + 22), S("insight", 120 + 40)],
    cta_card=S("cta", 45),
)


def build():
    sc = Bus()   # sonidos secos
    send = np.zeros(N)  # envío a reverb (mono)

    def sa(start, sig, g=1.0):
        n = min(len(sig), N - start)
        if n > 0:
            send[start:start + n] += sig[:n] * g
    drum = Bus()
    arp_bus = Bus()
    pad_bus = Bus()
    bass_bus = Bus()
    kick_times = []

    # --- Pad
    pads = [pad_chord(v) for v in PAD_VOICING]
    nbars = int(np.ceil(TOTAL_BEATS / 4))
    for bar in range(nbars):
        b0 = bar * 4
        g = G(PAD_G, b0 + 1.0)
        pl, pr = pads[chord_of_bar(bar)]
        pad_bus.add((pl * g * 0.045, pr * g * 0.045), b2s(b0))

    # --- Dron grave del gancho (La)
    t = tt(5.4)
    env = np.minimum(1, t / 1.6) * np.clip((5.2 - t) / 0.8, 0, 1)
    drone = np.sin(2 * np.pi * 55 * t) + 0.5 * lp(saw_add(110, t, K=10, rolloff=1.4), 400, 2)
    bass_bus.add(drone * env * 0.30, 0, 0.30)

    # --- Metrónomo del gancho (tic tac)
    for b in range(0, 10):
        sc.add(tick(2200 if b % 2 == 0 else 3000), b2s(b), 0.16 * min(1, 0.4 + b * 0.1), pan=0.0)

    # --- Kick, bajo, hi-hats, palmas
    k = kick()
    h_c, h_o, cl = hat(False), hat(True), clap()
    bass_cache = {}
    for b in range(0, int(TOTAL_BEATS)):
        bar, pos = divmod(b, 4)
        in_g = span(b, GROOVE)
        if in_g:
            drum.add(k, b2s(b), 0.62 * G(KICK_G, b))
            kick_times.append(b)
            # bajo en el contratiempo
            m = BASS_ROOT[chord_of_bar(bar)]
            if m not in bass_cache:
                bass_cache[m] = bass_note(m)
            bass_bus.add(bass_cache[m], b2s(b + 0.5), 0.55 * G(BASS_G, b))
            if pos == 0 and b >= 99:
                bass_bus.add(bass_cache[m], b2s(b), 0.35 * G(BASS_G, b))
        if span(b, HAT_SPANS):
            drum.add(h_o, b2s(b + 0.5), 0.17 * G(HAT_G, b), pan=0.25)
        if span(b, HAT16_SPANS):
            drum.add(h_c, b2s(b + 0.25), 0.12 * G(HAT_G, b), pan=-0.3)
            drum.add(h_c, b2s(b + 0.75), 0.12 * G(HAT_G, b), pan=0.3)
        if span(b, CLAP_SPANS) and pos in (1, 3):
            drum.add(cl, b2s(b), 0.24 * G(CLAP_G, b), pan=0.0)
            sa(b2s(b), cl, 0.12 * G(CLAP_G, b))

    # --- Arpegio
    pl_cache = {}
    vel = [1.0, 0.55, 0.78, 0.55]
    b = 19.0
    while b < 116:
        step, oct_ = arp_mode(b)
        bar = int(b // 4)
        tones = ARP_TONES[chord_of_bar(bar)]
        idx = int(round((b % 4) / step)) % 8 if step == 0.5 else int(round((b % 4) / step)) % 16 % 8
        m = tones[ARP_P8[idx]] + oct_
        if m not in pl_cache:
            pl_cache[m] = pluck(m)
        beat_pos = (b % 1) / 0.25
        v = vel[int(round(beat_pos)) % 4] if step == 0.25 else (1.0 if (b % 1) == 0 else 0.7)
        g = G(ARP_G, b) * v
        pan = 0.35 if int(round(b / step)) % 2 == 0 else -0.35
        arp_bus.add(pl_cache[m], b2s(b), 0.14 * g, pan=pan)
        sa(b2s(b), pl_cache[m], 0.05 * g)
        b += step

    # delay estéreo cruzado (corchea con puntillo) sobre el arpegio
    d1, d2 = int(0.375 * SR), int(0.75 * SR)
    al, ar = arp_bus.l.copy(), arp_bus.r.copy()
    al[d1:] += 0.34 * arp_bus.r[:-d1]
    ar[d1:] += 0.34 * arp_bus.l[:-d1]
    al[d2:] += 0.14 * arp_bus.l[:-d2]
    ar[d2:] += 0.14 * arp_bus.r[:-d2]
    arp_bus.l, arp_bus.r = al, ar

    # --- sidechain: el kick "hunde" pad, bajo y arpegio
    duck = np.ones(N)
    seg = np.exp(-tt(BEAT) / 0.11)
    for kb in kick_times:
        s0 = b2s(kb)
        n = min(len(seg), N - s0)
        duck[s0:s0 + n] *= 1 - 0.55 * seg[:n]
    for bus, d in ((pad_bus, 1.0), (bass_bus, 0.7), (arp_bus, 0.45)):
        dk = 1 - d * (1 - duck)
        bus.l *= dk
        bus.r *= dk
    # el pad también alimenta la reverb
    send += (pad_bus.l + pad_bus.r) * 0.30

    # --- Efectos de transición y de animación
    # whoosh + golpe de llegada en cada corte
    for key in ("purpose", "data", "python", "excel", "stress", "result", "insight", "cta"):
        f0 = START[key]
        w = whoosh(0.5)
        sc.add(w, f2s(f0), 0.22, pan=0.0)
        sa(f2s(f0), w, 0.10)
        imp = impact(1.6, 0.8)
        sc.add(imp, f2s(f0 + TR), 0.20)
        sa(f2s(f0 + TR), imp, 0.06)

    def hit(frame, g=0.5, dur=2.4, depth=1.0):
        imp = impact(dur, depth)
        sc.add(imp, f2s(frame), g)
        sa(f2s(frame), imp, 0.10)

    def add_bell(frame, midi, g=0.12, dur=1.6, pan=0.0, wet=0.55, bright=1.0):
        bl = bell(midi_hz(midi), dur, bright)
        sc.add(bl, f2s(frame), g, pan=pan)
        sa(f2s(frame), bl, g * wet)

    def add_pop(frame, g=0.10, f0=820, pan=0.0):
        sc.add(pop_snd(f0), f2s(frame), g, pan=pan)

    # Gancho
    hit(30, 0.62, 2.6)
    hit(60, 0.50, 2.4)
    for i, fr in enumerate(EV["hook_count_price"]):
        sc.add(tick(1500 + 140 * i), f2s(fr), 0.07)
    for i, fr in enumerate(EV["hook_count_model"]):
        sc.add(tick(1700 + 160 * i), f2s(fr), 0.07)
    r = riser(2 * (150 - 62) / FPS / 2 * 1.0, 1900)
    sc.add(r, f2s(EV["drop_riser"][0]), 0.20)
    sa(f2s(62), r, 0.06)
    hit(150, 0.55, 2.2, 0.9)  # entra el ritmo

    # Propósito
    for i, fr in enumerate(EV["purpose_chips"]):
        add_pop(fr, 0.11, 700 + 90 * i, pan=-0.2)

    # Datos: acordes de campana ascendentes (La menor pentatónica)
    for i, (fr, m) in enumerate(zip(EV["data_rows"], (81, 84, 88, 91, 93))):
        add_pop(fr, 0.09, 760, pan=-0.3)
        add_bell(fr + 2, m, 0.11, 1.4, pan=0.2 * (i - 2) / 2)

    # Python
    for i, fr in enumerate(EV["py_rows"]):
        sc.add(tick(2000 + 90 * i, 0.03), f2s(fr), 0.07, pan=0.3)
    for fr in EV["py_type1"] + EV["py_type2"]:
        sc.add(key_click(), f2s(fr), 0.20, pan=-0.1)
    for i, (fr, m) in enumerate(zip(EV["py_checks"], (81, 84, 88))):
        add_bell(fr, m, 0.12, 1.4)
    add_pop(EV["py_chip"], 0.10, 700)

    # Excel
    for i, fr in enumerate(EV["excel_cards"]):
        add_pop(fr, 0.11, 640 + 120 * i, pan=-0.25 + 0.5 * i)
    add_pop(EV["excel_plus"], 0.08, 520)
    hit(EV["excel_result"], 0.55, 2.6)
    for m in (69 + 12, 72 + 12, 76 + 12):          # acorde brillante La-Do-Mi
        add_bell(EV["excel_result"], m, 0.10, 2.2, wet=0.7)
    for fr, m in zip(EV["excel_bars"], (76, 81, 84)):
        sc.add(pluck(m + 12, 0.6), f2s(fr), 0.20)
        add_bell(fr, m + 12, 0.07, 1.2)
    add_bell(EV["excel_check"], 88, 0.12, 1.6)
    add_bell(EV["excel_check"] + 4, 93, 0.09, 1.6)

    # Pruebas de estrés
    for i, fr in enumerate(EV["peers_rows"]):
        add_pop(fr, 0.10, 640 + 80 * i, pan=-0.2)
    hit(EV["peers_result"], 0.45, 2.0, 0.9)
    add_bell(EV["peers_result"], 88, 0.10, 1.6)
    for i, fr in enumerate(EV["mc_count"]):
        sc.add(tick(1200 + 70 * i, 0.02), f2s(fr), 0.05, pan=0.2)
    r2 = riser((EV["mc_riser"][1] - EV["mc_riser"][0] + 12) / FPS, 2300)
    sc.add(r2, f2s(EV["mc_riser"][0] - 12), 0.20)
    sa(f2s(EV["mc_riser"][0] - 12), r2, 0.05)
    hit(EV["mc_hit"], 0.55, 2.4)
    add_bell(EV["mc_pct"], 93, 0.12, 1.8)
    for fr, m in zip(EV["q_gauges"], (81, 84)):
        add_pop(fr, 0.08, 700)
    for i, m in enumerate((81, 84, 88, 93)):
        add_bell(EV["q_check"] + 3 * i, m, 0.10, 1.8)

    # Resultado
    for i, fr in enumerate(EV["res_rows"]):
        add_pop(fr, 0.09, 600 + 90 * i, pan=-0.2)
    gl = glide(1800, 300, 0.5)
    sc.add(gl, f2s(EV["res_line"] - 6), 0.10)
    hit(EV["res_line"], 0.5, 2.2)

    # Conclusión
    for fr in EV["ins_pops"]:
        add_pop(fr, 0.10, 760, pan=-0.2)
    gl2 = glide(380, 760, (EV["ins_glide"][1] - EV["ins_glide"][0]) / FPS)
    sc.add(gl2, f2s(EV["ins_glide"][0]), 0.10)
    r3 = riser((EV["bus_riser"][1] - EV["bus_riser"][0]) / FPS, 2600)
    sc.add(r3, f2s(EV["bus_riser"][0]), 0.20)
    sa(f2s(EV["bus_riser"][0]), r3, 0.06)
    hit(EV["bus_drop"], 0.70, 2.8)
    for i, fr in enumerate(EV["bus_pops"]):
        add_pop(fr, 0.09, 680 + 80 * i, pan=-0.2)

    # Cierre
    hit(EV["cta_card"], 0.5, 3.0, 0.9)
    for m in (69 + 12, 72 + 12, 76 + 12, 81 + 12):
        add_bell(EV["cta_card"], m, 0.09, 3.2, wet=0.75)

    # --- Reverb común
    irl, irr = make_ir()
    wet_l = fftconv(send, irl)
    wet_r = fftconv(send, irr)

    return dict(
        drum=(drum.l, drum.r), sfx=(sc.l, sc.r), pad=(pad_bus.l, pad_bus.r), bass=(bass_bus.l, bass_bus.r),
        arp=(arp_bus.l, arp_bus.r), wet=(wet_l, wet_r),
    )


LEVELS = dict(drum=0.62, sfx=1.0, pad=2.6, bass=0.60, arp=2.8, wet=1.8)
DRIVE = 1.5


def master(stems, lv=None):
    lv = {**LEVELS, **(lv or {})}
    mix_l = sum(stems[k][0] * lv[k] for k in stems)
    mix_r = sum(stems[k][1] * lv[k] for k in stems)
    tb = np.arange(N) / SR / BEAT
    fade = np.interp(tb, [0, 0.4, 115.0, 118.0], [0.0, 1.0, 1.0, 0.0])
    mix_l = hp(mix_l * fade, 28, 2)
    mix_r = hp(mix_r * fade, 28, 2)
    mix_l = mix_l + 0.78 * hp(mix_l, 3200, 1)   # high-shelf: +5 dB de brillo
    mix_r = mix_r + 0.78 * hp(mix_r, 3200, 1)
    peak = max(np.abs(mix_l).max(), np.abs(mix_r).max())
    mix_l, mix_r = mix_l / peak, mix_r / peak
    mix_l = np.tanh(mix_l * DRIVE) / np.tanh(DRIVE)
    mix_r = np.tanh(mix_r * DRIVE) / np.tanh(DRIVE)
    return mix_l, mix_r


def write_wav(path, l, r, target_rms_db=-17.0, peak_db=-1.0):
    st = np.stack([l, r], axis=1)
    rms = np.sqrt(np.mean(st ** 2))
    g = 10 ** (target_rms_db / 20) / rms
    pk = np.abs(st).max() * g
    lim = 10 ** (peak_db / 20)
    if pk > lim:
        g *= lim / pk   # el techo manda sobre el RMS objetivo
    st = st * g
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return 20 * np.log10(np.sqrt(np.mean(st ** 2))), 20 * np.log10(np.abs(st).max()), st


def section_rms(stems, lv=None):
    """RMS (dBFS) de cada pista en cada escena, para equilibrar la mezcla."""
    lv = {**LEVELS, **(lv or {})}
    names = list(START)
    ends = list(START.values())[1:] + [TOTAL_FRAMES]
    print("pista".ljust(7) + "".join(n[:7].rjust(8) for n in names))
    for k in stems:
        row = k.ljust(7)
        for a, z in zip(START.values(), ends):
            seg = np.concatenate([stems[k][0][f2s(a):f2s(z)], stems[k][1][f2s(a):f2s(z)]]) * lv[k]
            row += f"{20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9):8.1f}"
        print(row)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "public/music.wav")
    out.parent.mkdir(parents=True, exist_ok=True)
    cache = Path(__file__).with_name("stems_cache.npz")
    print(f"{TOTAL_FRAMES} frames = {TOTAL_FRAMES / FPS:.2f} s, {TOTAL_BEATS:.0f} tiempos, {N} muestras")
    if "--remix" in sys.argv and cache.exists():
        z = np.load(cache)
        stems = {k: (z[k + "_l"], z[k + "_r"]) for k in ("drum", "sfx", "pad", "bass", "arp", "wet")}
    else:
        stems = build()
        np.savez(cache, **{k + "_l": v[0] for k, v in stems.items()}, **{k + "_r": v[1] for k, v in stems.items()})
    if "--rms" in sys.argv:
        section_rms(stems)
    l, r = master(stems)
    rms_db, pk_db, st = write_wav(out, l, r)
    print(f"escrito {out}  RMS {rms_db:.1f} dBFS  pico {pk_db:.1f} dBFS  ({out.stat().st_size / 1e6:.1f} MB)")
    if "--plot" in sys.argv:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        mono = st.mean(axis=1)
        win = SR // 4
        env = np.sqrt(np.convolve(mono ** 2, np.ones(win) / win, mode="same"))
        t = np.arange(N) / SR
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.plot(t[::200], 20 * np.log10(env[::200] + 1e-6), lw=0.8)
        for k, v in START.items():
            ax.axvline(v / FPS, color="r", lw=0.6)
            ax.text(v / FPS + 0.1, -10, k, fontsize=7, rotation=90, va="top")
        ax.set_ylim(-60, -5)
        ax.set_xlabel("s")
        ax.set_ylabel("RMS dBFS")
        fig.savefig(sys.argv[sys.argv.index("--plot") + 1], dpi=110, bbox_inches="tight")
