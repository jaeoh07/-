# 효과음 + 음악 트랙 생성: python3 sfx.py  →  sfx.wav (16.5초, 44.1kHz 스테레오)
# 흔한 쿵/휙/지지직/심장박동 대신 피아노·현악·마림바·유리·레코드 같은 소리로 구성
# 타이밍은 intro.html 의 T 와 맞춰져 있음
import wave
import numpy as np

SR = 44100
DUR = 16.5
rng = np.random.default_rng(11)
fx = np.zeros(int(SR * DUR))     # 효과음
music = np.zeros(int(SR * DUR))  # 음악(피치카토 리듬, 브이로그 BGM)

T = dict(crack=1.15, crazy=1.3, s2=2.6, s2B=3.0, s2C=3.85, s3=5.3, nums=[5.6, 5.8, 6.0, 6.2],
         s4=7.3, shock=8.45, s5=9.6, cols=[9.65, 10.0, 10.35, 10.7], freeze=12.6, s6=13.0,
         v1=13.15, v2=13.9, v3=14.5)


def add(sig, at, gain=1.0, buf=None):
    buf = fx if buf is None else buf
    i = int(round(at * SR))
    if i < 0:
        sig, i = sig[-i:], 0
    n = min(len(sig), len(buf) - i)
    if n > 0:
        buf[i:i + n] += sig[:n] * gain


def env_t(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, cutoff):
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):
        acc = (1 - a[k]) * x[k] + a[k] * acc
        y[k] = acc
    return y


def note(name):
    names = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
    return 440 * 2 ** ((names[name[:-1]] + (int(name[-1]) - 4) * 12) / 12)


# ── 악기
def pluck(f, dur=0.6, bright=0.5, damp=0.996):
    # Karplus-Strong 현 뜯는 소리 (피치카토/우쿨렐레)
    n = int(dur * SR)
    N = max(2, int(SR / f))
    buf = lowpass(rng.uniform(-1, 1, N), 1500 + 9000 * bright)
    y = np.zeros(n)
    y[:N] = buf[:n]
    for k in range(N, n):
        y[k] = damp * 0.5 * (y[k - N] + y[k - N - 1])
    return y * np.minimum(1, (dur - env_t(dur)) / 0.02)


def piano(f, dur=2.0, vel=1.0):
    # 가산 합성 피아노: 배음마다 살짝 어긋남(inharmonicity) + 해머 소리
    t = env_t(dur)
    s = np.zeros_like(t)
    for k in range(1, 10):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 16000:
            break
        s += np.sin(2 * np.pi * fk * t) * (1 / k ** 1.1) * np.exp(-t * (1.2 + k * 0.6))
    hammer = rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.3
    return (s + lowpass(hammer, 2500)) * np.minimum(1, t / 0.002) * vel


def taiko(dur=1.2):
    t = env_t(dur)
    f = 58 + 30 * np.exp(-t * 20)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5)
    mode2 = np.sin(2 * np.pi * np.cumsum(f * 1.59) / SR) * np.exp(-t * 9) * 0.4
    skin = lowpass(rng.standard_normal(len(t)), 500) * np.exp(-t * 30) * 2.0
    return np.tanh((body + mode2 + skin) * 1.6)


def marimba(f, dur=0.7):
    t = env_t(dur)
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.3 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 30)) * np.minimum(1, t / 0.002)


def ding(f, dur=1.0):
    # 띠링 (4단계용, 사용자 선택)
    t = env_t(dur)
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t * 4)
         + 0.15 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 7))
    return s * np.exp(-t * 3.5) * np.minimum(1, t / 0.003)


# ── 효과음
def mouse_click():
    def tick(f):
        t = env_t(0.012)
        n = rng.standard_normal(len(t))
        return ((n - lowpass(n, 3000)) * 0.6 + np.sin(2 * np.pi * f * t) * 0.5) * np.exp(-t * 500)
    out = np.zeros(int(0.06 * SR))
    a = tick(3200)
    out[:len(a)] += a
    j = int(rng.uniform(0.03, 0.045) * SR)
    b = tick(2600) * 0.6
    out[j:j + len(b)] += b[:len(out) - j]
    return out


def tinnitus(dur):
    # 귀 울리는 고음: 답답함/스트레스
    t = env_t(dur)
    f = 3800 + 500 * t / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2 * 0.15


def glass(dur=1.4):
    t = env_t(dur)
    s = np.zeros_like(t)
    for _ in range(70):   # 파편 하나하나 짤랑
        st = int(rng.uniform(0, 0.35) ** 1.6 * SR)
        f = rng.uniform(2500, 9500)
        tt = t[:len(t) - st]
        s[st:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(18, 60)) * rng.uniform(0.2, 1)
    n = rng.standard_normal(len(t))
    crash = (n - lowpass(n, 2500)) * np.exp(-t * 9)
    return s * 0.12 + crash * 0.7


def slide(dur=0.22):
    # 쓱: 종이/카드 미끄러지는 마찰음
    t = env_t(dur)
    n = rng.standard_normal(len(t))
    band = lowpass(n, 4500) - lowpass(n, 1200)
    return band * np.minimum(1, t / 0.03) * np.exp(-t * 14) * 2.2


def cello_drone(dur, f=55.0):
    t = env_t(dur)
    vib = f * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * t))
    ph = np.cumsum(vib) / SR
    saw = 2 * (ph % 1.0) - 1 + 0.5 * (2 * ((ph * 2.003) % 1.0) - 1)
    return lowpass(saw, 300 + 900 * t / dur) * (t / dur) ** 1.8


def record_scratch(dur=0.42):
    t = env_t(dur)
    rate = np.sin(np.pi * t / dur) * (1 + 0.6 * np.sin(2 * np.pi * 11 * t))
    f = 180 + 1400 * np.abs(rate)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    n = rng.standard_normal(len(t))
    hiss = (lowpass(n, 6000) - lowpass(n, 1200)) * np.abs(rate)
    return (tone * 0.5 + hiss * 0.8) * np.minimum(1, (dur - t) / 0.05)


def snap():
    t = env_t(0.06)
    n = rng.standard_normal(len(t))
    return (lowpass(n, 4000) - lowpass(n, 1500)) * np.exp(-t * 90) * 2.5


def piano_slam(at, size=1.0):
    # 피아노 저음 클러스터를 손바닥으로 내려치듯 + 북
    for nm in ['A0', 'A1', 'E2', 'A2', 'C3']:
        add(piano(note(nm), 2.4, 0.55), at, size)
    add(taiko(), at, 0.8 * size)


# ── 0. 탭 지옥: 광클 + 귀 울림 → 유리 박살
clicks = np.cumsum(0.16 * np.exp(-np.linspace(0, 2.3, 22)))
for c in clicks[clicks < T['crack'] - 0.03]:
    add(mouse_click(), c, 1.0)
add(tinnitus(T['crack']), 0, 1.6)
add(glass(), T['crack'], 0.9)
piano_slam(T['crazy'], 1.0)

# ── 2~3. 피치카토 리듬 (A단조) 이 몽타주~카운트를 끌고 감
bpm = 132
e8 = 60 / bpm / 2
riff = ['A2', 'A3', 'E3', 'A3', 'C4', 'A3', 'E3', 'A3', 'F2', 'F3', 'C3', 'F3', 'A3', 'F3', 'C3', 'G3']
for k, at in enumerate(np.arange(T['s2'], T['s4'] - 0.05, e8)):
    nm = riff[k % len(riff)]
    add(pluck(note(nm), 0.45, 0.35, 0.993), at, 0.55 if k % 2 == 0 else 0.38, music)
    if k % 8 == 0:
        add(piano(note(nm[:-1] + '1'), 0.9, 0.35), at, 1.0, music)
add(taiko(0.8), T['s2B'], 0.5)
add(piano(note('A1'), 1.2, 0.5), T['s2B'])
for nm in ['A3', 'C4', 'E4', 'A4']:
    add(pluck(note(nm), 0.6, 0.7, 0.995), T['s2C'], 0.45)
add(taiko(0.8), T['s2C'], 0.6)
for i, at in enumerate(T['nums'][:3]):
    add(marimba(note(['A4', 'C5', 'E5'][i])), at, 0.55)
add(slide(), T['nums'][3] - 0.05, 0.8)
add(marimba(note('A5'), 0.9), T['nums'][3] + 0.08, 0.35)

# ── 4. 리듬 뚝 → 첼로 드론으로 조임 → 0.25초 완전 정적 → 피아노 강타
gap = 0.25
add(cello_drone(T['shock'] - gap - T['s4']), T['s4'], 0.55)
piano_slam(T['shock'], 1.15)

# ── 5. 1~3단계는 현 + 쓱, 4단계는 띠링 / 밑에 피치카토가 작게 다시 깔림
for k, at in enumerate(np.arange(T['s5'], T['freeze'] + 0.4, e8)):
    nm = riff[k % len(riff)]
    add(pluck(note(nm), 0.45, 0.3, 0.993), at, 0.3 if k % 2 == 0 else 0.2, music)
for i, at in enumerate(T['cols'][:3]):
    add(slide(0.2), at - 0.04, 0.5 + i * 0.1)
    add(pluck(note(['E4', 'A4', 'C5'][i]), 0.7, 0.7, 0.996), at + 0.03, 0.55)
add(slide(0.2), T['cols'][3] - 0.04, 0.6)
add(ding(659.3), T['cols'][3] + 0.1, 0.45)
add(ding(880.0, 0.9), T['cols'][3] + 0.22, 0.5)

# ── 6. 레코드 끼익: 음악이 테이프처럼 느려지며 멈춤 → 브이로그 BGM
f0, f1 = int(T['freeze'] * SR), int((T['freeze'] + 0.4) * SR)
seg = np.arange(f1 - f0) / SR
pos = seg - seg ** 2 / (2 * 0.4)                       # 재생 속도 1 → 0
music[f0:f1] = np.interp(T['freeze'] + pos, np.arange(len(music)) / SR, music) * np.linspace(1, 0.3, f1 - f0)
music[f1:] = 0
add(record_scratch(), T['freeze'], 0.6)

ukulele = [('C', ['C4', 'E4', 'G4', 'C5']), ('G', ['B3', 'D4', 'G4', 'D5']), ('Am', ['C4', 'E4', 'A4', 'E5']), ('F', ['C4', 'F4', 'A4', 'F5'])]
beat = 60 / 100
at = T['s6'] + 0.05
bar = 0
while at < DUR - 0.2:
    name, tones = ukulele[bar % 4]
    for k in range(8):
        tt = at + k * beat / 2
        if tt >= DUR - 0.2:
            break
        add(pluck(note(tones[[0, 2, 1, 3, 2, 1, 3, 2][k]]), 0.5, 0.8, 0.994), tt, 0.45, music)
        if k in (2, 6):
            add(snap(), tt, 0.25, music)
    add(piano(note(tones[0][:-1] + '2'), 1.4, 0.25), at, 1.0, music)
    at += 4 * beat
    bar += 1
fade = int(0.6 * SR)
music[-fade:] *= np.linspace(1, 0, fade)
add(marimba(note('E5'), 0.5), T['v3'] + 0.15, 0.25)   # 형광펜 칠할 때 톡

# 리버브(간단한 컨볼루션)로 공간감
def reverb(x, amount, length=1.4, decay_rate=4.0):
    ir_t = env_t(length)
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * decay_rate)
    ir[0] = 0
    wet = np.fft.irfft(np.fft.rfft(x, 2 * len(x)) * np.fft.rfft(ir, 2 * len(x)))[:len(x)]
    return x + wet * amount * np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)


mix = reverb(fx, 0.22) + reverb(music, 0.12) * 0.75

# 충격적입니다 직전 0.25초는 잔향까지 완전히 비움
g0, g1 = int((T['shock'] - gap) * SR), int(T['shock'] * SR) - 30
mix[g0:g0 + 1323] *= np.linspace(1, 0, 1323)
mix[g0 + 1323:g1] = 0

# 마스터: 소프트 리미터, -1 dBFS
mix = np.tanh(mix * 1.2)
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
