from fastapi import FastAPI
from fastapi.responses import FileResponse
import random, re, time, os
from gtts import gTTS
from pydub import AudioSegment
import numpy as np

app = FastAPI()

CORPUS_FILE = "corpus.txt"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
def replace_words_with_noise(file_path, segments, amplitude=0.8):
    """
    segments: [(start_ms, end_ms), ...] 标记词对应的时间段
    amplitude: 噪声幅度比例（0~1），基于 int16 最大值
    """
    audio = AudioSegment.from_mp3(file_path)
    max_val = 32767  # int16 最大值

    for start, end in segments:
        duration_ms = end - start
        num_samples = int(audio.frame_rate * duration_ms / 1000) * audio.channels

        # 生成固定响度的白噪声
        noise_samples = np.random.normal(0, amplitude * max_val, num_samples)
        noise_samples = np.clip(noise_samples, -32768, 32767).astype(np.int16)

        noisy_segment = AudioSegment(
            noise_samples.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        )

        # 完全替换原片段
        audio = audio[:start] + noisy_segment + audio[end:]

    filename = f"noisy_{int(time.time()*1000)}.mp3"
    output_path = os.path.join(OUTPUT_DIR, filename)
    audio.export(output_path, format="mp3")
    return output_path

def load_corpus():
    corpus = []
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split("|")]
            if len(parts) == 3:
                corpus.append({
                    "text": parts[0],
                    "level": int(parts[1]),
                    "domain": parts[2]
                })
    return corpus

def parse_marked_sentence(sentence):
    marked_words = re.findall(r"\[(.*?)\]", sentence)
    plain_text = re.sub(r"[\[\]]", "", sentence)
    return plain_text, marked_words

def generate_tts_audio(text):
    filename = f"tts_{int(time.time()*1000)}.mp3"
    output_path = os.path.join(OUTPUT_DIR, filename)
    tts = gTTS(text=text, lang="zh")
    tts.save(output_path)
    return output_path

def calc_segments_by_chars(text, total_audio_length_ms):
    plain_text = re.sub(r"[\[\]]", "", text)
    total_chars = len(plain_text)
    per_char_ms = total_audio_length_ms / total_chars

    segments = []
    current_char_index = 0
    tokens = re.split(r"(\[.*?\])", text)

    for token in tokens:
        if not token:
            continue
        if token.startswith("[") and token.endswith("]"):
            word = token[1:-1]
            start_ms = current_char_index * per_char_ms
            end_ms = (current_char_index + len(word)) * per_char_ms
            segments.append((int(start_ms), int(end_ms)))
            current_char_index += len(word)
        else:
            current_char_index += len(token)

    return segments

def add_noise_to_segments(file_path, segments, amplitude=0.8):
    audio = AudioSegment.from_mp3(file_path)
    max_val = 32767  # int16 最大值

    for start, end in segments:
        duration_ms = end - start
        num_samples = int(audio.frame_rate * duration_ms / 1000) * audio.channels

        # 固定响度噪声
        noise_samples = np.random.normal(0, amplitude * max_val, num_samples)
        noise_samples = np.clip(noise_samples, -32768, 32767).astype(np.int16)

        noisy_segment = AudioSegment(
            noise_samples.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        )

        audio = audio[:start] + noisy_segment + audio[end:]

    filename = f"noisy_{int(time.time()*1000)}.mp3"
    output_path = os.path.join(OUTPUT_DIR, filename)
    audio.export(output_path, format="mp3")
    return output_path

@app.get("/random_audio")
def random_audio():
    corpus = load_corpus()
    if not corpus:
        return {"error": "corpus.txt 为空"}

    s = random.choice(corpus)
    plain_text, _ = parse_marked_sentence(s["text"])
    tts_file = generate_tts_audio(plain_text)
    total_ms = AudioSegment.from_mp3(tts_file).duration_seconds * 1000
    segments = calc_segments_by_chars(s["text"], total_ms)
    noisy_file = replace_words_with_noise(tts_file, segments, amplitude=0.8)


    return FileResponse(noisy_file, media_type="audio/mpeg", filename=os.path.basename(noisy_file))
