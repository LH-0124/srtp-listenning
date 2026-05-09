# T00_repo_audit — 仓库审查任务

## 角色

你是项目审查员，只做审查和报告，原则上不改业务代码。

## 开始前必须读取

- `AGENTS.md`
- `docs/PROJECT_STATE.md`
- `docs/STATE_MACHINE.md`
- `.codex/shared_state.json`

## 目标

确认仓库真实进度、可运行性、主要风险和下一步优先级。

## 执行步骤

1. 查看目录结构：

```bash
find . -maxdepth 4 -type f | sort
```

Windows PowerShell 可用：

```powershell
Get-ChildItem -Recurse -File | Select-Object FullName
```

2. 检查 Python 可编译性：

```bash
python -m py_compile data_pipeline/*.py server/*.py
```

3. 检查 requirements 是否足够：

```bash
pip install -r requirements.txt
```

4. 检查数据库结构：

```bash
python - <<'PY'
import sqlite3
conn = sqlite3.connect("capd_database.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cur.fetchall())
for (name,) in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print("\nTABLE", name)
    for row in cur.execute(f"PRAGMA table_info({name})"):
        print(row)
conn.close()
PY
```

5. 审查以下文件：

- `data_pipeline/preprocess.py`
- `data_pipeline/context_scoring.py`
- `data_pipeline/llm_augment.py`
- `data_pipeline/database_manager.py`
- `data_pipeline/run_pipeline.py`
- `server/main.py`
- `server/models.py`
- `server/audio_service.py`
- `server/adaptive_logic.py`

## 输出

创建或更新：

- `docs/AUDIT_REPORT.md`
- `.codex/logs/T00_result.md`
- `.codex/shared_state.json`

## 验收标准

`docs/AUDIT_REPORT.md` 至少包含：

1. 当前完成度估计；
2. 代码能否编译；
3. 安全问题；
4. API 问题；
5. 数据库问题；
6. 语料 pipeline 问题；
7. 音频噪声问题；
8. 下一步任务排序。

## 状态更新

完成后把 `.codex/shared_state.json` 中 `T00_repo_audit.status` 改为 `done` 或 `blocked`。
