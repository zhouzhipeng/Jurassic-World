"""Reproducible original weather ambience. Standard library only; run with Python."""
from array import array
from math import sin, pi, exp
from pathlib import Path
from random import Random
import wave

ROOT = Path(__file__).resolve().parents[1] / "assets" / "audio"
RATE = 22050


def write(name, samples):
    pcm = array("h", (round(max(-0.98, min(0.98, s)) * 32767) for s in samples))
    with wave.open(str(ROOT / name), "wb") as output:
        output.setparams((1, 2, RATE, 0, "NONE", "not compressed"))
        output.writeframes(pcm.tobytes())


def rain():
    # Filtered broadband rainfall, soft gusts, and seamless overlap at the loop.
    rng = Random(91521)
    length, overlap = RATE * 12, RATE // 2
    low, samples = 0.0, []
    for n in range(length + overlap):
        noise = rng.uniform(-1, 1)
        low += 0.16 * (noise - low)
        t = n / RATE
        gust = 0.8 + 0.1 * sin(2 * pi * t / 12) + 0.07 * sin(2 * pi * t / 4)
        samples.append((0.22 * noise + 0.55 * low) * gust)
    for n in range(overlap):
        blend = n / overlap
        samples[n] = samples[length + n] * (1 - blend) + samples[n] * blend
    write("weather-rain.wav", samples[:length])


def thunder():
    rng = Random(82013)
    low, samples = 0.0, []
    for n in range(RATE * 5):
        t = n / RATE
        noise = rng.uniform(-1, 1)
        low += 0.025 * (noise - low)
        envelope = min(1, t / 0.06) * exp(-t * 0.95) * min(1, (5 - t) / 0.7)
        rolling = 0.76 + 0.24 * sin(2 * pi * t * 2.3)
        samples.append((low * 2.2 + sin(2 * pi * 42 * t) * 0.16 + noise * exp(-t * 8) * 0.16) * envelope * rolling)
    write("weather-thunder.wav", samples)


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    rain()
    thunder()
    print("Created weather-rain.wav (12 s loop) and weather-thunder.wav (5 s).")
