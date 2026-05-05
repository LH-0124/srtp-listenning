#!/usr/bin/env bash
set -euo pipefail

# 用法：
#   bash scripts/codex_run_all.sh
#
# 说明：
# 1. 这个脚本会按顺序把任务文件交给 codex exec。
# 2. 每一步结束后，请人工检查 git diff 和 .codex/shared_state.json。
# 3. 初学阶段不建议一次跑完整个脚本；建议先逐条复制执行。

mkdir -p .codex/logs

# T00：只审查，不大改代码。read-only 更安全。
codex exec --sandbox read-only "$(cat .codex/tasks/T00_repo_audit.md)" \
  --output-last-message .codex/logs/T00_codex_output.md

# T01：允许写仓库，修复格式、安全和启动问题。
codex exec --sandbox workspace-write "$(cat .codex/tasks/T01_repo_stabilize.md)" \
  --output-last-message .codex/logs/T01_codex_output.md

# T02：实现 API 契约。
codex exec --sandbox workspace-write "$(cat .codex/tasks/T02_api_contract.md)" \
  --output-last-message .codex/logs/T02_codex_output.md

# T03：整理 pipeline。可以和 T04/T05 分支并行，但初学建议顺序执行。
codex exec --sandbox workspace-write "$(cat .codex/tasks/T03_data_pipeline.md)" \
  --output-last-message .codex/logs/T03_codex_output.md

# T04：优化音频噪声。
codex exec --sandbox workspace-write "$(cat .codex/tasks/T04_audio_noise.md)" \
  --output-last-message .codex/logs/T04_codex_output.md

# T05：补齐用户数据。
codex exec --sandbox workspace-write "$(cat .codex/tasks/T05_user_data.md)" \
  --output-last-message .codex/logs/T05_codex_output.md

# T06：测试、文档、演示。
codex exec --sandbox workspace-write "$(cat .codex/tasks/T06_tests_docs_release.md)" \
  --output-last-message .codex/logs/T06_codex_output.md

echo "全部 Codex 任务已执行完。请运行：git diff && pytest -q"
