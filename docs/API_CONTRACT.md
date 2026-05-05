# API_CONTRACT.md — 小程序后端接口契约草案

Base URL：

```text
http://127.0.0.1:8000
```

生产环境后续替换为服务器域名。

## 1. GET /health

用途：健康检查。

响应：

```json
{
  "status": "ok",
  "service": "srtp-capd-backend",
  "version": "0.1.0"
}
```

## 2. POST /api/v1/sessions

用途：创建训练会话。

请求：

```json
{
  "user_id": "demo_user",
  "training_mode": "LOW",
  "noise_profile": "none"
}
```

响应：

```json
{
  "session_id": "uuid",
  "user_id": "demo_user",
  "training_mode": "LOW",
  "difficulty": {
    "speed": 1.0,
    "snr": 20
  }
}
```

## 3. GET /api/v1/tasks/next

用途：获取下一道训练题。

查询参数：

- `session_id`: string, required

响应：

```json
{
  "task_id": "uuid",
  "session_id": "uuid",
  "text_hash": "sha256",
  "target_text": "演示阶段可返回",
  "audio_url": "http://127.0.0.1:8000/static/task_xxx.wav",
  "difficulty": {
    "speed": 1.0,
    "snr": 20,
    "noise_profile": "none"
  }
}
```

## 4. POST /api/v1/answers

用途：提交用户听写结果。

请求：

```json
{
  "session_id": "uuid",
  "task_id": "uuid",
  "user_input": "用户输入"
}
```

响应：

```json
{
  "correct": false,
  "score": 0.0,
  "message": "回答错误，难度降低",
  "new_difficulty": {
    "speed": 0.9,
    "snr": 23
  }
}
```

## 5. GET /api/v1/users/{user_id}/progress

用途：查询用户训练进度。

响应：

```json
{
  "user_id": "demo_user",
  "total_answers": 10,
  "correct_count": 7,
  "accuracy": 0.7,
  "current_difficulty": {
    "speed": 1.2,
    "snr": 16
  }
}
```

## 6. GET /openapi.json

用途：导出 OpenAPI JSON，给小程序前端或接口调试工具使用。
