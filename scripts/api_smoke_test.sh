#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
USER_ID="${USER_ID:-smoke_user}"

curl -fsS "$BASE_URL/health" >/dev/null

SESSION_JSON=$(curl -fsS -X POST "$BASE_URL/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"$USER_ID\",\"training_mode\":\"LOW\",\"noise_profile\":\"none\"}")
SESSION_ID=$(python -c "import json,sys; print(json.load(sys.stdin)['session_id'])" <<<"$SESSION_JSON")

TASK_JSON=$(curl -fsS "$BASE_URL/api/v1/tasks/next?session_id=$SESSION_ID")
TASK_ID=$(python -c "import json,sys; print(json.load(sys.stdin)['task_id'])" <<<"$TASK_JSON")
TARGET_TEXT=$(python -c "import json,sys; print(json.load(sys.stdin)['target_text'])" <<<"$TASK_JSON")

curl -fsS -X POST "$BASE_URL/api/v1/answers" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"task_id\":\"$TASK_ID\",\"user_input\":\"$TARGET_TEXT\"}" >/dev/null

curl -fsS "$BASE_URL/api/v1/users/$USER_ID/progress"
