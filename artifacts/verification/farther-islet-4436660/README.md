# 远海小岛验收

- 源码版本：`44366608d4c8860a7f33e883e062bf5cb45be321`（Move explorable islet farther offshore）
- 修改范围：`scenes/Game/scene.settings`、`scenes/Game/external-events/CoastalVoyage.events`
- 小岛中心从 `(7700, -1000, 0)` 移到 `(9500, -1000, 0)`，向东增加 1800 个游戏单位；靠岸范围、活动边界、探索判定及读档船位同步移动。船初始位置保持在水上的 `(6150, -1000, -50)`。
- `validate_project_files`：通过；结构、事件代码生成、扩展代码、JavaScript 检查和语义检查均通过。
- `verify_project_change`：`runtimeVerified=true`，`completionReady=true`；船和小岛各 1 个实例，位置有限，运行错误 0，3D 网格可见，贴图失败及对象拒绝均为 0。
- 手动帧推进：从主岛岸边上船，驶至船位 `(8681.67, -1000)`；下船后角色位于 `(8981.67, -1000, 25)`；走到 `(9360.83, -1000, 25)` 探索，再返回乘船。返航后在船位 `(6196.5, -901.41)` 下船，角色位于 `(5746.5, -901.41, 0)`。
- 画面复核：[海面间距](sea-gap.png)、[小岛登陆](landfall.png)。两张图片来自该源码版本的新预览，画布截图 3196×1800，质量检查无异常。
