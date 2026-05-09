import os
import uuid

import edge_tts
import librosa
import soundfile as sf

from server.noise_profiles import mix_with_snr, stable_noise_seed


ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


class AudioService:
    @staticmethod
    async def generate_task_audio(
        text: str,
        speed: float,
        snr: float,
        noise_profile: str = "none",
        seed: int | None = None,
    ) -> str:
        """
        Generate task audio and return the saved asset filename.

        Noise is deterministic when seed is provided. Without an explicit seed,
        a stable seed is derived from text, speed, SNR, and noise profile.
        """
        temp_filename = f"temp_{uuid.uuid4()}.mp3"
        temp_path = os.path.join(ASSETS_DIR, temp_filename)

        try:
            communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
            await communicate.save(temp_path)

            y, sr = librosa.load(temp_path, sr=None, mono=True)
            if abs(speed - 1.0) > 0.01:
                y = librosa.effects.time_stretch(y, rate=speed)

            noise_seed = (
                seed
                if seed is not None
                else stable_noise_seed(text, speed, snr, noise_profile)
            )
            y_out = mix_with_snr(
                y,
                sample_rate=sr,
                snr=snr,
                noise_profile=noise_profile,
                seed=noise_seed,
            )

            final_filename = f"task_{uuid.uuid4()}.wav"
            final_path = os.path.join(ASSETS_DIR, final_filename)
            sf.write(final_path, y_out, sr)
            return final_filename
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
