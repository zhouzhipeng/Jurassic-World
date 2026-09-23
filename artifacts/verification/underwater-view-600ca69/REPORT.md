# 潜水水下视野验收

源码版本：`600ca69`（Show underwater view while diving）。以下路径均相对于项目根目录。

## 改动

- `scenes/Game/external-events/CameraVisibility.events`：潜水时把第三人称镜头放到水面以下，并缩短观察距离。
- `materials/CoastalOcean.tsl.ts`：镜头在水下时降低海面遮挡。
- `tests/CoastalSwimming.js`：验证潜水和上浮时的镜头高度。
- `docs/COASTAL_SWIMMING.md`：更新操作与效果说明。

## 当前版本验证

- `validate_tsl_file` 对 `assets/environment/coastal-ocean.glb` 的 model 级验证通过，`activation_ready=true`。
- `validate_project_files` 结构、事件代码生成、扩展代码生成、JavaScript 与语义检查均通过。
- `tests/CoastalSwimming.js`：11 项断言通过；潜水镜头 Z≈−174（海面 Z=−80），上浮后 Z≈412。
- `verify_project_change`：`runtimeVerified=true`、`completionReady=true`；运行时错误、贴图失败和对象拒收均为 0。
- `dive.png`：正常预览中按 C 下潜后的画面，显示玩家、水面下方与近海地形。
