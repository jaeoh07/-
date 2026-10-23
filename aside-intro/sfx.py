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


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def glitch(dur=0.42):
    # 디지털 지지직: 짧은 조각마다 다른 음/노이즈, 사이사이 끊김
    n = int(dur * SR)
    y = np.zeros(n)
    i = 0
    while i < n:
        seg = int(SR * rng.uniform(0.012, 0.035))
        t = np.arange(min(seg, n - i)) / SR
        kind = rng.integers(3)
        if kind == 0:
            y[i:i + len(t)] = np.sign(np.sin(2 * np.pi * rng.uniform(200, 2500) * t)) * 0.6
        elif kind == 1:
            y[i:i + len(t)] = rng.standard_normal(len(t)) * 0.7
        i += seg
    return np.round(y * 6) / 6  # 비트크러시


def reverse_swell(dur):
    # 거꾸로 감기는 빨려 들어가는 소리
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = lowpass(rng.standard_normal(n), 800 + 9000 * t ** 2)
    return noise * t ** 3


def stab(freqs, dur, decay, bright=4000):
    # 디스토션 걸린 톱니파 화음 한 방
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(saw(f * d, t) for f in freqs for d in (0.995, 1.0, 1.006))
    s = lowpass(s, bright * np.exp(-t * 3) + 300)
    return np.tanh(s * 1.5) * np.exp(-t * decay) * np.minimum(1, t / 0.004)


def mystery(dur):
    # 4단계: 불협화음(트라이톤) 서스펜스 스팅 + 위쪽 반짝이는 음, 떨리며 길게 남음
    n = int(dur * SR)
    t = np.arange(n) / SR
    trem = 1 + 0.25 * np.sin(2 * np.pi * 7 * t)
    low = stab([65.4, 92.5, 123.5], dur, 1.2, 2500) * trem
    shimmer = (np.sin(2 * np.pi * 1975 * t) + np.sin(2 * np.pi * 2794 * t)) * 0.12 * np.exp(-t * 1.5)
    return low + shimmer


# 초반: 지지직 글리치로 시선 잡기 → 미쳤습니다에 빨려들어가는 소리 + 강한 한 방
add(glitch(), 0.0, 0.55)
add(reverse_swell(0.5), 0.25, 0.7)
add(stab([110, 164.8, 220], 0.9, 4.5), 0.75, 0.75)
add(whoosh(0.3, 2000, 9000), 0.62, 0.5)

# 충격적입니다 / 1~3단계는 휙
# whoosh 는 가운데가 가장 크므로 장면 시점보다 dur/2 먼저 시작
def swoosh(at, dur, gain, lo=300, hi=5000):
    add(whoosh(dur, lo, hi), at - dur / 2, gain)


swoosh(6.8, 0.6, 1.0, 200, 4000)             # 충격적입니다
for i, at in enumerate([7.8, 8.3, 8.75]):    # 1~3단계, 점점 크게
    swoosh(at + 0.08, 0.32, 0.5 + i * 0.12, 500, 7000)

# 4단계 ???: 빨려 들어가다가 불길한 화음
add(reverse_swell(0.4), 8.75, 0.6)
add(mystery(0.85), 9.15, 0.8)

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
