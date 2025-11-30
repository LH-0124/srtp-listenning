import edge_tts
import librosa
import soundfile as sf
import numpy as np
import os
import uuid

# 设置资源保存路径
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

class AudioService:
    @staticmethod
    async def generate_task_audio(text: str, speed: float, snr: float) -> str:
        """
        生成最终的音频文件路径
        1. TTS 生成
        2. Librosa 变速 & 加噪
        """
        # 1. TTS 生成临时文件
        temp_filename = f"temp_{uuid.uuid4()}.mp3"
        temp_path = os.path.join(ASSETS_DIR, temp_filename)
        
        communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
        await communicate.save(temp_path)
        
        # 2. 后期处理 (变速 + 加噪)
        # 加载音频 (sr=None 保持原始采样率)
        y, sr = librosa.load(temp_path, sr=None)
        
        # A. 变速 (Time Stretch)
        if abs(speed - 1.0) > 0.01:
            y = librosa.effects.time_stretch(y, rate=speed)
            
        # B. 加噪 (Add Noise)
        # 生成白噪声
        noise = np.random.randn(len(y))
        # 计算功率
        signal_power = np.mean(y ** 2)
        noise_power = np.mean(noise ** 2)
        # 根据SNR计算需要的噪音功率
        target_noise_power = signal_power / (10 ** (snr / 10))
        scale = np.sqrt(target_noise_power / noise_power)
        # 混合
        y_out = y + noise * scale
        
        # 3. 保存最终文件
        final_filename = f"task_{uuid.uuid4()}.wav"
        final_path = os.path.join(ASSETS_DIR, final_filename)
        sf.write(final_path, y_out, sr)
        
        # 清理临时文件
        os.remove(temp_path)
        
        return final_filename