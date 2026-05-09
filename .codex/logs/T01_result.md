# T01_repo_stabilize result

完成时间：2026-05-05T22:19:06+08:00

## 完成内容

- 移除了 `data_pipeline/llm_augment.py` 中硬编码 API Key 默认值。
- `llm_augment.py` 现在通过 `python-dotenv` 加载 `.env`，并从环境变量读取 `OPENAI_API_KEY`、`GPT_API_URL`、`GPT_MODEL`。
- 新增 `.env.example`，只包含占位配置，不包含真实密钥。
- 确认 `requirements.txt` 包含 `python-dotenv`。
- 补充 `.gitignore`，忽略 `.env`、虚拟环境、`__pycache__`、`.pyc`、生成音频和 `.codex/logs/*.jsonl`。
- 在 `server/main.py` 中显式确保 `assets/` 目录存在后再挂载静态目录。
- 未新增 `/api/v1` 接口，未重构业务逻辑。

## 安全检查

已排除 `.env`、`.codex/logs/**`、原始大语料、二进制音频和 `.pyc` 后执行 secret 扫描：

- `rg ... 'sk-[A-Za-z0-9_-]{20,}' .`
- `rg ... 'Bearer [A-Za-z0-9._-]{20,}' .`
- `rg ... 'OPENAI_API_KEY\s*=\s*["''][^"'']{8,}["'']' .`
- `rg ... '(api[_-]?key|token|password|secret)\s*[:=]\s*["''][^"'']{8,}["'']' .`

结果：未发现硬编码 API Key 或明显敏感值。

## 验证命令

- `rg -n '^python-dotenv$' requirements.txt`
  - 通过。
- `python -m compileall -q data_pipeline server`
  - 通过。
- `python -c "import server.main; print('server import ok')"`
  - 通过，输出 `server import ok`。
- `bash -lc "python -m py_compile data_pipeline/*.py server/*.py"`
  - 当前 Windows 环境拒绝创建 Bash/WSL 实例，失败原因：`E_ACCESSDENIED`。
- `python -m py_compile data_pipeline/*.py server/*.py`
  - PowerShell 下通配符不展开，失败原因：Python 收到字面量 `data_pipeline/*.py`。
- `Get-ChildItem -Path data_pipeline,server -Filter *.py | ForEach-Object { python -m py_compile $_.FullName; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE } }`
  - 通过，已等价编译 `data_pipeline/` 和 `server/` 下所有 Python 文件。
- `python -m uvicorn server.main:app --host 127.0.0.1 --port 8011`
  - 短时启动 smoke 通过，随后已停止。
- `python -m uvicorn server.main:app --reload --host 127.0.0.1 --port 8012`
  - 短时启动 smoke 通过，随后已停止。

## 剩余风险

- PowerShell 不能直接展开 `python -m py_compile data_pipeline/*.py server/*.py` 中的通配符；在 Windows PowerShell 下应使用文件枚举命令，或在可用的 Git Bash 中运行原命令。
- 本次按用户指定的 PowerShell 命令复核，`python -m compileall -q data_pipeline server` 已通过。
- `/api/v1`、用户数据表、持久化答题记录、音频噪声 profile 仍属于后续 T02/T05/T04 范围。
- `__pycache__` 是编译验证产生或刷新出的构建产物，不属于业务代码变更。
