# T01_repo_stabilize — 仓库稳定化与安全修复

## 角色

你是 Python 后端工程师。目标是让仓库能安装、能编译、能启动，并修复安全风险。

## 依赖

必须先完成 `T00_repo_audit`。

## 目标

1. 修复 Python 文件格式和明显语法问题；
2. 移除硬编码 API Key；
3. 增加 `.env.example`；
4. 确保 `assets/` 自动创建；
5. 提供可启动命令；
6. 不改变业务逻辑的大方向。

## 建议改动

### 1. Secret 管理

将所有 key 改为：

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
```

创建 `.env.example`：

```env
OPENAI_API_KEY=replace_me
GPT_API_URL=https://api.openai.com/v1/chat/completions
GPT_MODEL=gpt-3.5-turbo
DATABASE_URL=sqlite:///./capd_database.db
ASSETS_BASE_URL=http://localhost:8000/static
```

更新 `.gitignore`，至少包含：

```gitignore
.env
.venv/
__pycache__/
*.pyc
assets/*.mp3
assets/*.wav
.codex/logs/*.jsonl
```

### 2. 编译检查

运行：

```bash
python -m py_compile data_pipeline/*.py server/*.py
```

### 3. 最小启动检查

运行：

```bash
python -m uvicorn server.main:app --reload
```

若不能启动，修复 import path、assets 目录、数据库路径问题。

## 输出

- 修改代码；
- 更新 `.env.example`、`.gitignore`；
- 写 `.codex/logs/T01_result.md`；
- 更新 `.codex/shared_state.json`。

## 验收标准

- `python -m py_compile data_pipeline/*.py server/*.py` 通过；
- `python -m uvicorn server.main:app --reload` 能启动；
- 仓库中无硬编码 key；
- `.env.example` 存在。
