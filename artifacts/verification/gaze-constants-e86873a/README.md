# 注视描述 Constants 验收

- 源码修订：`e86873a4aa5657199a93d7044343d9e6d28a9783`（`Store gaze descriptions in project constants`）。
- 修改范围：`constants.toml`、`scenes/Game/scene.settings`、`scenes/Game/external-events/GazeDescription.events`。
- `constants.toml` 的 `[gazeDescriptions]` 保存 15 个物体的完整两行中文文案。场景变量的字符串子项引用各常量路径；事件只读取变量，不含硬编码中文文案。
- TOML 独立解析成功；15 条文案与 15 个占位符键一致。
- `validate_project_files`：`valid=true`；结构、事件生成、扩展生成代码、JavaScript 作者检查和语义检查均通过。
- `verify_project_change`：重新加载 `Game`，暂停预览 `preview-ws-32`，推进 3 帧；`runtimeVerified=true`、`completionReady=true`。描述对象数量 1、坐标有限、运行时错误数 0。
- 将相机朝向营地工作台后推进 30 帧，预览显示从 Constants 解析的「营地工作台」及其说明：[截图](camp-forge.png)。

未验证每一条文案的独立视觉呈现；此次运行时复核覆盖营地工作台。
