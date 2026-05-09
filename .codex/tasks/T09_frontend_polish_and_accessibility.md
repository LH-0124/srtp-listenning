# T09_frontend_polish_and_accessibility — 前端体验优化

## 角色

你是 UI/UX 工程师。目标是把本地 demo 页面从“能用”提升到“适合演示和交互”。

## 开始前必须读取

- `AGENTS.md`
- `.codex/shared_state.json`
- `docs/API_CONTRACT.md`
- `docs/TECHNICAL_OVERVIEW.md`
- `docs/NEXT_PHASE_PLAN.md`
- `.codex/logs/T07_result.md`
- `.codex/logs/T08_result.md`
- `.codex/tasks/T09_frontend_polish_and_accessibility.md`

## 依赖

必须等 `T08_frontend_api_flow_demo` 完成。

## 目标

1. 优化页面布局和视觉风格；
2. 完善白天/黑夜模式；
3. 完善 loading、error、success、empty 状态；
4. 让桌面和移动端都可用；
5. 增加清晰的 API 调试信息区域；
6. 保证文本不重叠，按钮和输入控件易用；
7. 不改后端业务逻辑。

## 设计要求

- 页面第一屏就是可用训练界面，不做营销 landing page；
- 避免花哨渐变堆砌，优先清晰、稳定、适合康复训练；
- 白天模式要明亮但不刺眼；
- 黑夜模式要低眩光；
- 控件状态要明显；
- 移动端布局不能溢出；
- 不引入构建工具。

## 验收命令

```powershell
python -m compileall -q data_pipeline server tests
pytest -q
python -c "import server.main; print('server import ok')"
```

人工验收：

- 打开 `/`；
- 切换白天/黑夜模式；
- 测试不同窗口宽度；
- 跑一遍 T08 的完整流程；
- 检查错误状态是否清晰。

## 输出

- 更新 `.codex/shared_state.json`
- 写 `.codex/logs/T09_result.md`

## 禁止事项

- 不要改 API；
- 不要改数据库；
- 不要引入大型前端框架；
- 不要提交生成音频或本地隐私文件。
