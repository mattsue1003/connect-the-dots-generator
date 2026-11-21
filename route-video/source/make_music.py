"""Original background music for the route video (64 s, 96 BPM, C major).

Fully synthesized here with numpy, so it has no third-party copyright.
Structure follows the video: intro pad (0-5 s), driving groove (5-45 s),
lift (45-49 s), aerial finale with bell melody (49-64 s), fade out.
Usage: python3 make_music.py out.wav
"""
import sys, wave
import numpy as np

SR = 44100
DUR = 64.0
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N)
Rch = np.zeros(N)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 - pan))
    Rch[i:i + len(sig)] += sig * np.sqrt(0.5 * (1 + pan))


def env_adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s)
    e[:a] = np.linspace(0, 1, a, endpoint=False) if a else e[:a]
    e[a:a + d] = np.linspace(1, s, len(e[a:a + d]))
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


# chords: C  G/B  Am  F  (one per bar), voicings in MIDI
CHORDS = [
    [48, 55, 60, 64, 67],  # C
    [47, 55, 59, 62, 67],  # G/B
    [45, 52, 57, 60, 64],  # Am
    [41, 53, 57, 60, 65],  # F
]
ROOTS = [36, 35, 33, 29]

NBARS = int(np.ceil(DUR / BAR))

# ---- pad (whole piece) ----
for b in range(NBARS):
    ch = CHORDS[b % 4]
    t0 = b * BAR
    n = int((BAR + 0.6) * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in ch[1:]:
        f = midi(m)
        for det in (-0.12, 0.12):
            ff = f * 2 ** (det / 12)
            sig += np.sin(2 * np.pi * ff * t) + 0.35 * np.sin(4 * np.pi * ff * t) + 0.12 * np.sin(6 * np.pi * ff * t)
    sig *= env_adsr(n, 0.5, 0.4, 0.8, 0.7)
    sig *= 0.035
    add(sig, t0, pan=-0.25)
    add(sig, t0 + 0.011, pan=0.25)

# ---- section helpers ----
GROOVE = (5.0, 60.0)  # drums / bass / arps active
FINALE = 49.0


def in_groove(t):
    return GROOVE[0] <= t < GROOVE[1]


# ---- bass ----
for b in range(NBARS):
    root = ROOTS[b % 4]
    for k in range(4):
        t0 = b * BAR + k * BEAT
        if not in_groove(t0):
            continue
        n = int(BEAT * 0.95 * SR)
        t = np.arange(n) / SR
        f = midi(root + (12 if k == 3 else 0))
        sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
        sig *= env_adsr(n, 0.008, 0.15, 0.55, 0.08) * 0.16
        add(sig, t0)

# ---- pluck arpeggio (8ths) ----
ARP = [0, 2, 3, 4, 3, 2, 1, 2]
for b in range(NBARS):
    ch = CHORDS[b % 4]
    for k in range(8):
        t0 = b * BAR + k * BEAT / 2
        if not in_groove(t0):
            continue
        m = ch[1 + ARP[k] % 4] + 12
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        f = midi(m)
        sig = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) * np.exp(-t * 18)) * np.exp(-t * 7)
        sig *= np.minimum(1, t / 0.003)
        add(sig * 0.055, t0, pan=0.35 if k % 2 else -0.35)

# ---- drums ----
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.5


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))  # crude highpass
    t = np.arange(n) / SR
    return x * np.exp(-t * (18 if open_ else 70)) * 0.032


def snap():
    n = int(0.2 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n) * np.exp(-t * 25) * 0.065
    x += np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.12
    return x


K, H, HO, S = kick(), hat(), hat(True), snap()
for b in range(NBARS):
    for k in range(8):
        t0 = b * BAR + k * BEAT / 2
        if not in_groove(t0):
            continue
        if k in (0, 4) or (k == 5 and b % 2):
            add(K, t0)
        if k in (2, 6):
            add(S, t0, pan=0.1)
        add(HO if k == 7 else H, t0, pan=0.3)

# ---- riser / swell into the finale (45-49 s) ----
n = int(4.0 * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n)
noise = np.diff(np.concatenate([[0], noise]))
add(noise * (t / 4.0) ** 2 * 0.06, 45.0, pan=0)
cym_n = int(2.5 * SR); ct = np.arange(cym_n) / SR
cym = np.diff(np.concatenate([[0], rng.standard_normal(cym_n)])) * np.exp(-ct * 2.2) * 0.07
add(cym, FINALE)

# ---- bell melody in the finale ----
MEL = [(0, 76, 1), (1, 79, 1), (2, 81, 2), (4, 79, 1), (5, 76, 1), (6, 74, 2),
       (8, 72, 1), (9, 74, 1), (10, 76, 2), (12, 74, 1), (13, 72, 1), (14, 72, 2)]
for rep in range(2):
    base = FINALE + rep * 4 * BAR  # 16 beats per phrase
    for beat, m, ln in MEL:
        t0 = base + beat * BEAT
        if t0 > DUR - 2:
            continue
        n = int(2.2 * SR); t = np.arange(n) / SR
        f = midi(m)
        sig = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12)
        sig *= np.exp(-t * 1.6) * np.minimum(1, t / 0.004)
        add(sig * 0.07, t0, pan=0.15)

# ---- simple reverb (FFT convolution with decaying noise IR) ----
def reverb(x, secs=2.2, mix=0.22):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 3.2)
    ir[:int(0.02 * SR)] = 0
    ir /= np.sqrt(np.sum(ir ** 2))
    m = len(x) + n
    nfft = 1 << (m - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    return x * (1 - mix) + wet * mix * 0.6

L2, R2 = reverb(L), reverb(Rch)

# master envelope: fade in 1.2 s, fade out last 4 s
t = np.arange(N) / SR
master = np.minimum(1, t / 1.2) * np.clip((DUR - t) / 4.0, 0, 1)
L2 *= master; R2 *= master
peak = max(np.abs(L2).max(), np.abs(R2).max())
L2, R2 = L2 / peak * 0.89, R2 / peak * 0.89

out = sys.argv[1] if len(sys.argv) > 1 else 'music.wav'
data = (np.stack([L2, R2], axis=1) * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(data.tobytes())
print('wrote', out)
