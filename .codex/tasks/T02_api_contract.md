# T02_api_contract — 小程序 API 契约与导出

## 角色

你是后端 API 工程师。目标是提供小程序可以稳定调用的接口。

## 依赖

必须先完成 `T01_repo_stabilize`。

## 目标

新增 `/api/v1` 接口，不破坏旧接口。

## 必须实现的接口

### 1. 健康检查

```http
GET /health
```

返回：

```json
{
  "status": "ok",
  "service": "srtp-capd-backend",
  "version": "0.1.0"
}
```

### 2. 创建训练会话

```http
POST /api/v1/sessions
Content-Type: application/json
```

请求：

```json
{
  "user_id": "demo_user",
  "training_mode": "LOW",
  "noise_profile": "none"
}
```

返回：

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

### 3. 获取下一题

```http
GET /api/v1/tasks/next?session_id=uuid
```

返回：

```json
{
  "task_id": "uuid",
  "session_id": "uuid",
  "text_hash": "sha256",
  "target_text": "演示阶段可返回；正式阶段建议隐藏",
  "audio_url": "http://localhost:8000/static/task_xxx.wav",
  "difficulty": {
    "speed": 1.0,
    "snr": 20,
    "noise_profile": "none"
  }
}
```

### 4. 提交答案

```http
POST /api/v1/answers
Content-Type: application/json
```

请求：

```json
{
  "session_id": "uuid",
  "task_id": "uuid",
  "user_input": "用户听写内容"
}
```

返回：

```json
{
  "correct": true,
  "score": 1.0,
  "message": "回答正确，难度提升",
  "new_difficulty": {
    "speed": 1.1,
    "snr": 18
  }
}
```

### 5. 查询用户进度

```http
GET /api/v1/users/{user_id}/progress
```

返回：

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

## API 文档

FastAPI 应自动提供：

- `/docs`
- `/redoc`
- `/openapi.json`

但你必须额外维护：

- `docs/API_CONTRACT.md`
- `docs/openapi-draft.yaml`

## 测试命令

启动服务后运行：

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/v1/sessions ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"demo_user\",\"training_mode\":\"LOW\"}"
```

Git Bash 写法：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/sessions   -H "Content-Type: application/json"   -d '{"user_id":"demo_user","training_mode":"LOW"}'
```

## 输出

- 修改 `server/main.py`、`server/models.py`，必要时新增 service/router 文件；
- 更新 `docs/API_CONTRACT.md`；
- 更新 `docs/openapi-draft.yaml`；
- 写 `.codex/logs/T02_result.md`；
- 更新 `.codex/shared_state.json`。
