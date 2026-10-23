# 효과음 + 비트 트랙 생성: python3 sfx.py  →  sfx.wav (12초, 44.1kHz 스테레오)
# 타이밍은 intro.html 의 T 와 맞춰져 있음
import wave
import numpy as np

SR = 44100
DUR = 12.0
rng = np.random.default_rng(7)
out = np.zeros(int(SR * DUR))
bed = np.zeros(int(SR * DUR))  # 비트는 따로 모아서 덕킹

T = dict(crazy=0.6, s2=1.7, s2B=2.15, s2C=3.0, s3=4.4, nums=[4.72, 4.92, 5.12, 5.32], s4=6.4,
         beats=[6.6, 6.85, 7.08, 7.28], shock=7.5, s5=8.7, cols=[8.75, 9.12, 9.45, 9.78], s6=11.45)


def add(sig, at, gain=1.0, buf=None):
    buf = out if buf is None else buf
    i = int(at * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def env_t(dur):
    return np.arange(int(dur * SR)) / SR


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


def saw(f, t):
    return 2 * ((f * t) % 1.0) - 1


def whoosh(dur=0.45, lo=300, hi=5000):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    cut = lo + (hi - lo) * np.sin(np.pi * t) ** 2
    s = lowpass(noise, cut) - lowpass(noise, cut * 0.25)
    return s * np.sin(np.pi * t) ** 1.5 * 2.5


def boom(dur=0.9, f0=140, f1=38, decay=4.0):
    t = env_t(dur)
    freq = f1 + (f0 - f1) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * decay)
    click = rng.standard_normal(len(t)) * np.exp(-t * 120) * 0.6
    return np.tanh((body + lowpass(click, 3000)) * 2.2)


def crack(dur=0.25):
    # 채찍/스네어 같은 날카로운 고음 노이즈
    t = env_t(dur)
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 1500)) * np.exp(-t * 22)


def stab(freqs, dur, decay, bright=4000):
    # 디스토션 걸린 톱니파 화음 한 방 (브라암)
    t = env_t(dur)
    s = sum(saw(f * d, t) for f in freqs for d in (0.995, 1.0, 1.006))
    s = lowpass(s, bright * np.exp(-t * 3) + 300)
    return np.tanh(s * 1.5) * np.exp(-t * decay) * np.minimum(1, t / 0.004)


def impact(at, size=1.0):
    # 쿵 + 브라암 + 크랙을 한 번에
    add(boom(1.2, 170, 32, 2.6), at, 1.0 * size)
    add(stab([55, 82.4, 110], 1.0, 3.5, 3000), at, 0.45 * size)
    add(crack(), at, 0.5 * size)


def reverse_swell(dur):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    return lowpass(rng.standard_normal(n), 800 + 9000 * t ** 2) * t ** 3


def glitch(dur=0.3):
    # 디지털 지지직: 짧은 조각마다 다른 음/노이즈, 사이사이 끊김
    n = int(dur * SR)
    y = np.zeros(n)
    i = 0
    while i < n:
        seg = int(SR * rng.uniform(0.012, 0.035))
        m = min(seg, n - i)
        t = np.arange(m) / SR
        kind = rng.integers(3)
        if kind == 0:
            y[i:i + m] = np.sign(np.sin(2 * np.pi * rng.uniform(200, 2500) * t)) * 0.6
        elif kind == 1:
            y[i:i + m] = rng.standard_normal(m) * 0.7
        i += seg
    return np.round(y * 6) / 6


def tick(f=1400, dur=0.08):
    t = env_t(dur)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 60)


def key_click():
    t = env_t(0.03)
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 2500)) * np.exp(-t * 250) * 0.8


def kick():
    t = env_t(0.35)
    freq = 45 + 110 * np.exp(-t * 30)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 9) * 1.8)


def hat():
    t = env_t(0.05)
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 7000)) * np.exp(-t * 90) * 0.5


def heartbeat():
    t = env_t(0.3)
    freq = 40 + 40 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 14)


def sub_drop(dur=1.0):
    t = env_t(dur)
    freq = 30 + 90 * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 2.2)


def beep(dur, f=1000):
    # 방송용 삐- 처리음
    t = env_t(dur)
    return np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.005) * np.minimum(1, (dur - t) / 0.01) * 0.45


def ding(f, dur=1.0):
    # 띠링: 종소리처럼 배음 섞인 사인파
    t = env_t(dur)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
         + 0.15 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 7))
    return s * np.exp(-t * 3.5) * np.minimum(1, t / 0.003)


def clock(f=2200):
    t = env_t(0.05)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 120)
    c = key_click()
    s[:len(c)] += c * 0.5
    return s


# ── 1. 훅: 지지직 → 빨려 들어감 → 미쳤습니다 쾅
add(glitch(0.28), 0.0, 0.6)
add(boom(0.6, 120, 40, 6), 0.0, 0.5)
add(reverse_swell(0.45), T['crazy'] - 0.45, 0.8)
impact(T['crazy'], 1.0)
add(glitch(0.14), 1.62, 0.5)
add(whoosh(0.35, 800, 9000), 1.55, 0.6)

# ── 2. 몽타주: 비트 + 창 뜨는 틱 + 타이핑
beat = 60 / 140
for k, at in enumerate(np.arange(T['s2'], T['s4'] - 0.05, beat)):
    add(kick(), at, 0.9, bed)
    add(hat(), at + beat / 2, 0.8, bed)
for k in range(16):
    add(tick(1800 + (k % 4) * 250, 0.04), T['s2'] + 0.04 + k * 0.055, 0.25)
for at in np.sort(rng.uniform(T['s2'] + 0.2, T['s3'] - 0.3, 34)):
    add(key_click(), at, 0.35)
add(boom(0.5, 150, 50, 7), T['s2B'], 0.6)
add(crack(0.18), T['s2B'], 0.35)
add(whoosh(0.3, 600, 8000), T['s2C'] - 0.15, 0.6)
add(boom(0.7, 160, 45, 5), T['s2C'], 0.75)
add(reverse_swell(0.5), T['s3'] - 0.5, 0.5)
add(glitch(0.11), 4.33, 0.45)

# ── 3. 카운트 1-2-3 → 4 는 쓱
for i, at in enumerate(T['nums'][:3]):
    add(tick(900 + i * 250, 0.1), at, 0.6)
    add(boom(0.25, 130, 60, 14), at, 0.4)
add(whoosh(0.3, 1500, 9000), T['nums'][3] - 0.12, 0.75)  # 쓱

# ── 4. 모든 소리 빠지고(정적) 심장박동 → 충격적입니다 초대형 쾅
add(sub_drop(1.2), T['s4'], 0.3)
for i, at in enumerate(T['beats']):
    add(heartbeat(), at, 0.4 + i * 0.08)
add(reverse_swell(0.6), T['shock'] - 0.6, 1.0)
impact(T['shock'], 1.0)
add(glitch(0.28), T['shock'], 0.5)
add(sub_drop(1.2), T['shock'] + 0.05, 0.6)

# ── 5. 1~4단계 휙, 4단계만 띠링으로 살짝 강조 → 엔딩
for i, at in enumerate(T['cols'][:3]):
    add(whoosh(0.32, 500, 7000), at - 0.1, 0.55 + i * 0.12)
    add(boom(0.35, 150 + i * 20, 55, 10), at + 0.05, 0.3 + i * 0.08)
add(whoosh(0.32, 500, 7000), T['cols'][3] - 0.1, 0.85)
add(ding(659.3), T['cols'][3] + 0.1, 0.45)          # 띠-링 (피치 살짝 낮춤)
add(ding(880.0, 0.9), T['cols'][3] + 0.22, 0.5)
add(glitch(0.16), 11.36, 0.45)
impact(T['s6'], 0.6)

# 리버브(간단한 컨볼루션)로 공간감
ir_t = env_t(1.1)
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 5)
ir[0] = 0
wet = np.fft.irfft(np.fft.rfft(out, 2 * len(out)) * np.fft.rfft(ir, 2 * len(out)))[:len(out)]
wet *= 0.18 * np.max(np.abs(out)) / np.max(np.abs(wet))
mix = out + wet + bed * 0.35

# 마스터: 소프트 리미터, -1 dBFS
mix = np.tanh(mix * 1.3)
mix *= 0.89 / np.max(np.abs(mix))
fade = int(0.04 * SR)
mix[-fade:] *= np.linspace(1, 0, fade)
stereo = np.stack([mix, mix], axis=1)
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((stereo * 32767).astype('<i2').tobytes())
print('sfx.wav written')
