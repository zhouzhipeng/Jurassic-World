# 钓鱼 UI 与动画核验

- 来源修订：`0ed430d`（`Place desktop fishing HUD below top notices`）；包含前置功能提交 `e274950`、触屏图层修正 `c7af3f2`。
- 场景：`Game`。运行时通过 `verify_project_change` 完成结构校验、项目重新载入和暂停预览；`runtimeVerified=true`、`completionReady=true`、运行错误数 0。
- 触屏模式按实际状态推进：待命 → 按 G 抛竿（`FishingState=1`，`AnimationState=14`）→ 等待 → 咬钩（`FishingState=2`，`AnimationState=16`）→ 按 G 收线（`FishingState=3`，`FishingResult=1`，`AnimationState=17`）。鱼肉 `Meat` 从 4 增加到 5。提前收线另行检查为 `FishingResult=-1`，面板显示“收线太早，稍后再试”，鱼肉未增加。
- 已目视检查当前修订截图：`artifacts/verification/fishing-ui/ready.png`、`cast.png`、`bite.png`、`catch.png`、`desktop.png`。触屏布局显示专用面板、进度条、鱼竿和结果；桌面布局将面板放在顶部通知下方。
- 资源：`assets/models/fishing-rod.glb`、`assets/models/survivor-animated.glb`、`assets/ui/fishing-panel.svg`、`assets/ui/fishing-meter.svg`；可编辑 Blender 源位于 `sources/models/`。
