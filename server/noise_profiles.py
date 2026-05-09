import hashlib
from typing import Literal

import numpy as np


NoiseProfileName = Literal["none", "white", "cafe", "street", "speech_babble"]

SUPPORTED_NOISE_PROFILES = ("none", "white", "cafe", "street", "speech_babble")
DEFAULT_TARGET_RMS = 0.12
PEAK_LIMIT = 0.95


def stable_noise_seed(text: str, speed: float, snr: float, noise_profile: str) -> int:
    payload = f"{text}|{speed:.4f}|{snr:.4f}|{noise_profile}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big", signed=False) % (2**32)


def apply_fade(audio: np.ndarray, sample_rate: int, fade_ms: float = 30.0) -> np.ndarray:
    if audio.size == 0:
        return audio
    fade_samples = int(sample_rate * fade_ms / 1000)
    fade_samples = min(fade_samples, audio.size // 2)
    if fade_samples <= 1:
        return audio

    faded = audio.copy()
    fade_in = np.linspace(0.0, 1.0, fade_samples, dtype=np.float32)
    fade_out = np.linspace(1.0, 0.0, fade_samples, dtype=np.float32)
    faded[:fade_samples] *= fade_in
    faded[-fade_samples:] *= fade_out
    return faded


def normalize_audio(
    audio: np.ndarray,
    *,
    target_rms: float = DEFAULT_TARGET_RMS,
    peak_limit: float = PEAK_LIMIT,
) -> np.ndarray:
    if audio.size == 0:
        return audio.astype(np.float32)

    normalized = np.nan_to_num(audio.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
    rms = float(np.sqrt(np.mean(normalized**2)))
    if rms > 1e-8 and target_rms > 0:
        normalized *= target_rms / rms

    peak = float(np.max(np.abs(normalized)))
    if peak > peak_limit:
        normalized *= peak_limit / peak

    return normalized.astype(np.float32)


def peak_value(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.max(np.abs(audio)))


def rms_value(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))


def generate_noise_profile(
    profile: str,
    length: int,
    sample_rate: int,
    rng: np.random.Generator,
) -> np.ndarray:
    if profile not in SUPPORTED_NOISE_PROFILES:
        raise ValueError(
            f"Unsupported noise_profile '{profile}'. "
            f"Expected one of {', '.join(SUPPORTED_NOISE_PROFILES)}."
        )
    if length <= 0 or profile == "none":
        return np.zeros(max(length, 0), dtype=np.float32)

    if profile == "white":
        noise = rng.normal(0.0, 1.0, length)
    elif profile == "cafe":
        noise = _cafe_noise(length, sample_rate, rng)
    elif profile == "street":
        noise = _street_noise(length, sample_rate, rng)
    else:
        noise = _speech_babble_noise(length, sample_rate, rng)

    noise = normalize_audio(noise, target_rms=1.0, peak_limit=1.0)
    return apply_fade(noise, sample_rate, fade_ms=50.0)


def mix_with_snr(
    signal: np.ndarray,
    *,
    sample_rate: int,
    snr: float,
    noise_profile: str,
    seed: int,
) -> np.ndarray:
    clean = normalize_audio(signal)
    if noise_profile == "none":
        return apply_fade(clean, sample_rate, fade_ms=10.0)

    rng = np.random.default_rng(seed)
    noise = generate_noise_profile(noise_profile, len(clean), sample_rate, rng)
    signal_rms = rms_value(clean)
    noise_rms = rms_value(noise)
    if signal_rms <= 1e-8 or noise_rms <= 1e-8:
        return apply_fade(clean, sample_rate, fade_ms=10.0)

    target_noise_rms = signal_rms / (10 ** (snr / 20.0))
    mixed = clean + noise * (target_noise_rms / noise_rms)
    mixed = normalize_audio(mixed)
    return apply_fade(mixed, sample_rate, fade_ms=10.0)


def _smooth_random(length: int, window: int, rng: np.random.Generator) -> np.ndarray:
    raw = rng.normal(0.0, 1.0, length)
    window = max(3, min(window, max(length // 2, 3)))
    kernel = np.ones(window, dtype=np.float32) / window
    return np.convolve(raw, kernel, mode="same")


def _cafe_noise(length: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
    base = _smooth_random(length, max(sample_rate // 35, 3), rng)
    chatter = _smooth_random(length, max(sample_rate // 120, 3), rng)
    envelope = rng.uniform(0.35, 1.0, length)
    envelope = np.convolve(envelope, np.ones(max(sample_rate // 8, 3)) / max(sample_rate // 8, 3), mode="same")
    clinks = np.zeros(length)
    event_count = max(1, length // max(sample_rate * 3, 1))
    for _ in range(event_count):
        start = int(rng.integers(0, max(length - 1, 1)))
        dur = int(rng.integers(max(sample_rate // 120, 1), max(sample_rate // 35, 2)))
        end = min(length, start + dur)
        if end > start:
            clinks[start:end] += rng.normal(0.0, 0.8, end - start) * np.hanning(end - start)
    return 0.55 * base + 0.35 * chatter * envelope + 0.1 * clinks


def _street_noise(length: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(length) / sample_rate
    rumble = (
        0.6 * np.sin(2 * np.pi * 42 * t + rng.uniform(0, 2 * np.pi))
        + 0.35 * np.sin(2 * np.pi * 77 * t + rng.uniform(0, 2 * np.pi))
    )
    wind = _smooth_random(length, max(sample_rate // 20, 3), rng)
    passbys = np.zeros(length)
    event_count = max(1, length // max(sample_rate * 2, 1))
    for _ in range(event_count):
        center = int(rng.integers(0, max(length, 1)))
        dur = int(rng.integers(max(sample_rate // 2, 1), max(sample_rate * 2, 2)))
        start = max(0, center - dur // 2)
        end = min(length, start + dur)
        if end > start:
            passbys[start:end] += rng.normal(0.0, 0.5, end - start) * np.hanning(end - start)
    return 0.45 * rumble + 0.35 * wind + 0.2 * passbys


def _speech_babble_noise(length: int, sample_rate: int, rng: np.random.Generator) -> np.ndarray:
    babble = np.zeros(length)
    for _ in range(6):
        carrier = _smooth_random(length, max(sample_rate // int(rng.integers(90, 170)), 3), rng)
        envelope = rng.uniform(0.0, 1.0, length)
        envelope = np.convolve(envelope, np.ones(max(sample_rate // 12, 3)) / max(sample_rate // 12, 3), mode="same")
        babble += carrier * envelope
    murmur = _smooth_random(length, max(sample_rate // 45, 3), rng)
    return 0.75 * babble + 0.25 * murmur
