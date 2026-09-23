# 小船初始水面位置验收

源码修订：`95aec2e60438d4d81a2d19b83ec1080177f4d39a`（`Place rowboat offshore at the starting beach`）。

修改 `scenes/Game/scene.settings` 中的初始船位与前一帧坐标，将主岛岸边的小船放在 `(6150, -1000, -50)`；同步修改 `scenes/Game/functions/sceneUpdate.events` 的读档、重生复位坐标，以及 `scenes/Game/external-events/CoastalVoyage.events` 的水域边界和主岛下船位置。

`validate_project_files` 的结构、事件生成、扩展生成代码、JavaScript authoring 和语义检查均通过。提交后 `verify_project_change` 返回 `runtimeVerified: true`、`completionReady: true`；小船位置有限，3D 图层有可见 mesh，纹理失败、渲染拒绝对象和运行错误均为 0。

在同一源码修订的新预览中，将玩家移动到岸边 `(5750, -1000)`。截图显示[小船位于水面](rowboat-offshore.png)。按 F 成功上船，玩家和船同在 `(6150, -1000)`；再次按 F 后玩家落在主岛陆地 `(5700, -1000, 0)`，船仍留在水面。

本次针对初始水面位置与主岛上下船进行了验证；小岛往返的历史验收见 `artifacts/verification/coastal-voyage-a6102cd/REPORT.md`，不作为该源码修订的验证证据。
