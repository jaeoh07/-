# 효과음 트랙 생성: python3 sfx.py  →  sfx.wav (10초, 44.1kHz 스테레오)
# 타이밍은 intro.html 의 T 와 맞춰져 있음
import wave
import numpy as np

SR = 44100
DUR = 10.0
rng = np.random.default_rng(7)
out = np.zeros(int(SR * DUR))


def add(sig, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sig), len(out) - i)
    out[i:i + n] += sig[:n] * gain


def lowpass(x, cutoff):
    # 시간에 따라 바뀌는 cutoff 를 받는 1차 로우패스
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):
        acc = (1 - a[k]) * x[k] + a[k] * acc
        y[k] = acc
    return y


def whoosh(dur=0.45, lo=300, hi=5000):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    cut = lo + (hi - lo) * np.sin(np.pi * t) ** 2
    s = lowpass(noise, cut) - lowpass(noise, cut * 0.25)
    return s * np.sin(np.pi * t) ** 1.5 * 2.5


def boom(dur=0.9, f0=140, f1=38, decay=4.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = f1 + (f0 - f1) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * decay)
    click = rng.standard_normal(n) * np.exp(-t * 120) * 0.6
    return np.tanh((body + lowpass(click, 3000)) * 2.2)


def tick(dur=0.12, f=1400):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 45) * 0.6


def riser(dur):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(180 + 900 * t ** 2) / SR)
    noise = lowpass(rng.standard_normal(n), 400 + 6000 * t ** 2)
    return (tone * 0.35 + noise * 0.8) * t ** 2.2


def drone(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 45 * t) + 0.5 * np.sin(2 * np.pi * 90.7 * t)
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.3)
    return s * env * 0.35


# 핵심 순간에만 휙: 미쳤습니다 / 충격적입니다 / 1~4단계
# whoosh 는 가운데가 가장 크므로 장면 시점보다 dur/2 먼저 시작
def swoosh(at, dur, gain, lo=300, hi=5000):
    add(whoosh(dur, lo, hi), at - dur / 2, gain)


swoosh(0.75, 0.5, 0.9)                       # 미쳤습니다
swoosh(6.8, 0.6, 1.0, 200, 4000)             # 충격적입니다
for i, at in enumerate([7.8, 8.3, 8.75]):    # 1~3단계, 점점 크게
    swoosh(at + 0.08, 0.32, 0.5 + i * 0.12, 500, 7000)
swoosh(9.23, 0.55, 1.1, 200, 4500)           # 4단계 ???

# 마스터: 소프트 리미터, -1 dBFS
out = np.tanh(out * 1.2)
out *= 0.89 / np.max(np.abs(out))
fade = int(0.04 * SR)
out[-fade:] *= np.linspace(1, 0, fade)
stereo = np.stack([out, out], axis=1)
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype('<i2').tobytes())
print('sfx.wav written')
