# 角色游泳动作重做验收

源码版本：`17294af`（含 `8eb9ea8`）。本文路径均相对于项目根目录。

## 范围

- `tools/add_swim_animations.py` 从 `sources/models/survivor-fishing-source.blend` 重建 `Swim` 与 `Dive`。
- `sources/models/survivor-swim-source.blend` 为可编辑动作源；`assets/models/survivor-animated.glb` 为游戏运行资源。
- `scenes/Game/external-events/CameraVisibility.events` 缩短水面游泳时的观察距离。
- `tests/CoastalSwimming.js` 检查实际播放的片段和游泳状态切换。

## 当前版本结果

- Blender 5.1 后台生成成功。安装后的 GLB 含原有 20 个动作、16 根骨骼、7 个网格和 7 个材质槽；`Swim`、`Dive` 名称保持不变。
- 两段动作第 1 帧与第 41 帧的采样姿势一致，循环接缝差小于 `1e-15`。
- `validate_project_files` 的结构、事件生成、扩展生成、JavaScript 和语义检查均通过。
- `tests/CoastalSwimming.js` 全部 14 项断言通过，包含 `Swim → Dive → Swim` 的实际模型动作切换。
- `verify_project_change` 返回 `runtimeVerified=true`、`completionReady=true`，运行时错误、贴图失败和对象拒收均为 0。
- `surface.png` 和 `dive.png` 为同一正常预览中的水面及按 C 潜水后的画面。
