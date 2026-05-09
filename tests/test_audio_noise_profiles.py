import numpy as np
import pytest

from server.noise_profiles import (
    SUPPORTED_NOISE_PROFILES,
    generate_noise_profile,
    mix_with_snr,
    peak_value,
    rms_value,
)


def test_supported_noise_profiles_are_stable():
    assert SUPPORTED_NOISE_PROFILES == (
        "none",
        "white",
        "cafe",
        "street",
        "speech_babble",
    )


@pytest.mark.parametrize("profile", SUPPORTED_NOISE_PROFILES)
def test_noise_profile_output_is_reproducible_non_silent_and_limited(profile):
    sample_rate = 16000
    t = np.linspace(0, 0.5, sample_rate // 2, endpoint=False, dtype=np.float32)
    signal = 0.2 * np.sin(2 * np.pi * 440 * t)

    mixed_a = mix_with_snr(
        signal,
        sample_rate=sample_rate,
        snr=12.0,
        noise_profile=profile,
        seed=1234,
    )
    mixed_b = mix_with_snr(
        signal,
        sample_rate=sample_rate,
        snr=12.0,
        noise_profile=profile,
        seed=1234,
    )

    assert np.allclose(mixed_a, mixed_b)
    assert rms_value(mixed_a) > 0.01
    assert peak_value(mixed_a) <= 0.95


def test_invalid_noise_profile_raises_clear_error():
    rng = np.random.default_rng(1)

    with pytest.raises(ValueError, match="Unsupported noise_profile"):
        generate_noise_profile("rain", 1000, 16000, rng)
