# README_CLI_WORKFLOW.md — Codex CLI 高阶玩法说明

## 1. 最基础交互模式

```bash
codex
```

进入后可以输入：

```text
请先阅读 AGENTS.md、docs/PROJECT_STATE.md、docs/STATE_MACHINE.md、.codex/shared_state.json，然后告诉我当前应该做哪个任务，不要改代码。
```

## 2. 计划模式

在 Codex CLI 里输入：

```text
/plan
```

然后说：

```text
请基于 .codex/tasks/T02_api_contract.md 先给出执行计划，不要修改代码。
```

适合复杂任务开始前先让它规划。

## 3. 非交互执行单个任务

```bash
codex exec --sandbox workspace-write "$(cat .codex/tasks/T02_api_contract.md)"   --output-last-message .codex/logs/T02_codex_output.md
```

含义：

- `codex exec`：非交互模式，适合自动执行；
- `--sandbox workspace-write`：允许 Codex 修改当前仓库；
- `$(cat 文件)`：把任务文件作为提示词；
- `--output-last-message`：把 Codex 最后总结写到日志文件。

## 4. 只读审查任务

```bash
codex exec --sandbox read-only "$(cat .codex/tasks/T00_repo_audit.md)"   --output-last-message .codex/logs/T00_codex_output.md
```

适合让 Codex 审查项目但不改代码。

## 5. 并行玩法：多个终端、多个任务

打开多个终端，但要遵守依赖：

终端 A：

```bash
codex exec --sandbox read-only "$(cat .codex/tasks/T00_repo_audit.md)"
```

T00 完成后，终端 B：

```bash
codex exec --sandbox workspace-write "$(cat .codex/tasks/T01_repo_stabilize.md)"
```

T01 完成后，T03/T04/T05 可以在不同 git worktree 或不同分支中并行。

初学者不要在同一个工作目录里同时让多个 Codex 写代码，容易互相覆盖。更安全的方式是使用 git worktree。

## 6. git worktree 并行示例

```bash
git worktree add ../srtp-api -b codex/api-contract
git worktree add ../srtp-pipeline -b codex/pipeline
git worktree add ../srtp-audio -b codex/audio
```

然后分别进入：

```bash
cd ../srtp-api
codex exec --sandbox workspace-write "$(cat .codex/tasks/T02_api_contract.md)"
```

```bash
cd ../srtp-pipeline
codex exec --sandbox workspace-write "$(cat .codex/tasks/T03_data_pipeline.md)"
```

```bash
cd ../srtp-audio
codex exec --sandbox workspace-write "$(cat .codex/tasks/T04_audio_noise.md)"
```

最后人工合并分支。

## 7. 让 Codex 自检查

每个任务 prompt 都要求它：

1. 修改代码；
2. 运行测试；
3. 更新共享状态；
4. 写日志；
5. 总结风险。

你还可以在任务完成后执行：

```bash
codex exec --sandbox read-only "请审查当前 git diff，指出 bug、安全问题、测试遗漏，不要修改代码。"
```

## 8. 常用 CLI 内部命令

在交互式 `codex` 里输入：

- `/status`：看当前模型、权限、上下文；
- `/diff`：看 Codex 改了什么；
- `/review`：让 Codex 审查当前改动；
- `/compact`：长对话压缩上下文；
- `/permissions`：调整权限；
- `/exit`：退出。

## 9. 初学者推荐执行顺序

不要一上来全自动。建议：

```bash
codex
```

然后粘贴：

```text
请阅读 AGENTS.md 和 .codex/tasks/T00_repo_audit.md，只做审查，不要修改代码。完成后写 docs/AUDIT_REPORT.md。
```

确认审查结果后，再运行 T01、T02。
