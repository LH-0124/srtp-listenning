# T04_audio_noise — 音频生成与噪声自然度优化

## 角色

你是音频处理工程师。目标是让训练音频更自然，而不是突兀叠加白噪声。

## 依赖

必须先完成 `T02_api_contract`。

## 当前问题

现有逻辑大概率是直接对 TTS 波形叠加随机白噪声，听感可能突兀、刺耳，也不接近真实训练环境。

## 目标

1. 支持至少 3 种 noise profile：
   - `none`
   - `white_soft`
   - `cafe`
   - `street`
2. 加入 fade in / fade out；
3. 做 RMS 归一化，避免爆音；
4. 根据 SNR 控制噪声强度；
5. 支持固定 seed，便于测试复现；
6. API 可传入 `noise_profile`。

## 实现建议

新增：

- `server/noise_profiles.py`
- `server/audio_service.py` 中调用 profile

噪声策略：

- `white_soft`：低幅度白噪声 + fade；
- `cafe`：多段低频/中频噪声混合，模拟人群底噪；
- `street`：低频 rumble + 稀疏瞬态事件；
- 所有噪声先归一化，再按 SNR 混合。

不要使用突然开始/突然结束的噪声。必须 fade in/out。

## 测试

新增或执行：

```bash
python - <<'PY'
import asyncio
from server.audio_service import AudioService

async def main():
    for p in ["none", "white_soft", "cafe", "street"]:
        name = await AudioService.generate_task_audio(
            "这是一个音频测试句子。",
            speed=1.0,
            snr=20,
            noise_profile=p
        )
        print(p, name)

asyncio.run(main())
PY
```

检查：

- 文件存在；
- 时长合理；
- 无明显爆音；
- none 模式无噪声；
- 多次固定 seed 输出可复现。

## 输出

- 修改音频相关文件；
- 更新 `docs/AUDIO_NOISE_DESIGN.md`；
- 写 `.codex/logs/T04_result.md`；
- 更新 `.codex/shared_state.json`。
