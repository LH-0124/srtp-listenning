# T05_user_data — 用户数据、会话与训练记录

## 角色

你是后端数据工程师。目标是补齐小程序需要的用户训练数据。

## 依赖

必须先完成 `T02_api_contract`。

## 目标

新增持久化数据结构，至少支持：

1. 用户；
2. 训练会话；
3. 训练题目；
4. 用户答案；
5. 用户进度。

## 数据库建议

### users

- `id`
- `user_id`
- `nickname`
- `created_at`

### training_sessions

- `id`
- `session_id`
- `user_id`
- `training_mode`
- `noise_profile`
- `speed`
- `snr`
- `created_at`
- `ended_at`

### training_tasks

- `id`
- `task_id`
- `session_id`
- `sentence_id`
- `target_text`
- `audio_url`
- `speed`
- `snr`
- `noise_profile`
- `created_at`

### answers

- `id`
- `answer_id`
- `session_id`
- `task_id`
- `user_input`
- `target_text`
- `correct`
- `score`
- `created_at`

### user_progress

- `id`
- `user_id`
- `total_answers`
- `correct_count`
- `accuracy`
- `current_speed`
- `current_snr`
- `updated_at`

## 注意

- MVP 阶段可以不用复杂登录，`user_id` 可由小程序传入 openid 或 demo id。
- 不要存真实敏感个人信息。
- 若没有迁移工具，先用 `database_manager.py` 做 `CREATE TABLE IF NOT EXISTS`。

## API 影响

确保：

- 创建 session 时写入 `training_sessions`；
- 获取下一题时写入 `training_tasks`；
- 提交答案时写入 `answers` 并更新 `user_progress`；
- 查询进度时从数据库读取。

## 输出

- 修改数据库管理文件；
- 修改 API；
- 更新 `docs/DATABASE_SCHEMA.md`；
- 写 `.codex/logs/T05_result.md`；
- 更新 `.codex/shared_state.json`。

## 验收标准

- 新用户创建 session 后数据库有记录；
- 获取下一题后数据库有 task 记录；
- 提交答案后数据库有 answer 记录；
- 进度接口能返回 accuracy。
