# 注视物体描述验收

- 源码修订：`be3074c36f280bb1ac67c2290a4f5f8e37cfd666`（`Keep gaze captions on visible surface targets`，基于 `e348119da24f0de6321d171071963418d817571c`）
- 范围：`scenes/Game/scene.settings`、`scenes/Game/objects/GazeDescription.settings`、`scenes/Game/external-events/GazeDescription.settings`、`scenes/Game/external-events/GazeDescription.events`、`scenes/Game/functions/sceneUpdate.events`
- GDevelop `validate_project_files`：`valid=true`，结构、事件代码生成、扩展生成代码、JavaScript 作者检查与语义检查均通过。
- `verify_project_change`：重新加载 `Game` 场景，暂停预览 `preview-ws-30`，推进 3 帧；`runtimeVerified=true`、`completionReady=true`。描述对象数量为 1、坐标有限、运行时错误数为 0。
- 手动复核：摄像机朝向营地工作台后推进 30 帧，卡片显示「营地工作台」及说明，位置在桌面上方；转向远离目标后推进 40 帧，卡片隐藏。

截图：[初始无目标](initial.png) · [工作台描述](surface-object.png) · [转向后隐藏](rotated-view.png)。

本次描述覆盖 `GazeTargets` 列出的地表资源、营地设施、船只和恐龙。矿洞内目标暂未纳入，以免在洞外透过洞壁显示描述；未验证全部场景物件的遮挡判定。
