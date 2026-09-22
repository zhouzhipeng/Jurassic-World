# 扩大山地地图性能优化验收

受测源码：`9e5b84005b4f3992ad822fbebd463b077ce17e4f`（`Focus distant actor rendering and shadows around exploration; document optimization`）。对照源码：`7026dcc`。本目录证据仅对应上述源码；证据提交不修改游戏。

## 改动

- `scenes/Game/functions/sceneUpdate.events`：删除滚轮缩放，保留旋转和自动避障。
- `scenes/Game/external-events/DistanceVisibility.events`：恐龙 32 米外隐藏、28 米内恢复；资源 42 米外隐藏、38 米内恢复；保留实例、血量和存档身份。
- `scenes/Game/external-events/FoliageLOD.events`、`MountainFoliage.events` 及四个 LOD 对象配置：远处植物停止绘制，靠近恢复；缓存未移动植物的地形高度。
- `scenes/Game/external-events/CameraVisibility.events`：相机射线直接查询原有 1 米山地三角网格；静态景物采用附近部件包围盒；交互植物保留精确模型检测。
- `scenes/Game/scene.settings`：中等阴影质量，阴影范围集中在附近 45 米。
- `tools/build_camera_bounds.py`、`assets/models/camera-scenery-bounds.json`：从可编辑 Blender 场景生成 1308 个相机避障包围盒。维护说明见 `docs/WORLD_PERFORMANCE.md`。

## 性能

相同参考机器、相同 `tests/CameraPerformance.js` 营地路线（移动 1400 单位，采样 240 帧）：平均帧耗时 **44.63 → 30.51 ms，降低 31.6%**。事件平均耗时 **28.45 → 14.00 ms**；采样末帧绘制调用 **1021 → 725**。最终围栏/屋檐路线平均 **22.84 ms**。两条路线均通过该参考机器的 33 ms 测试预算。

这些是确定性预览分析器结果，不等同于所有机器上的实时 FPS，也不代表已达到稳定 60 FPS。最终营地采样仍有 399.4 ms 的单帧峰值，围栏路线峰值 34 ms。

山地仍完整驻留，本次没有资产流式下载或卸载；减少的是绘制、动画和相机查询成本。保守景物包围盒在边角附近可能让镜头稍早收近。

## 验证

结构、事件代码生成、扩展代码和 JavaScript 作者 API 验证通过；提交后重新载入并运行 `verify_project_change`，运行时错误为 0，3D 对象可见，没有失败纹理和被拒绝对象，`runtimeVerified` / `completionReady` 均为 true。

逐项测试、操作 ID 和性能摘要见 `results.json`。`camp.png` 是当前源码营地截图，用于外观检查，不用于证明 FPS。

- `tests/DistanceVisibility.js`：37 项通过，包含远处隐藏、接近恢复、血量保留、山坡射线与实际网格交点一致。
- `tests/CameraPerformance.js`：8 项通过。
- `tests/MountainRadar.js`：22 项通过，包含爬坡、跳跃、骑乘和雷达位置。
- `tests/CameraSmoothFollow.js`：13 项通过，包含镜头平滑、遮挡透明、采集后隐藏。
- `tests/FoliageLOD.js`：38 项通过，包含远近切换、再生和重启。
- 新鲜预览中设置 `CameraDistance=1250`，注入 `mouseWheel delta_y=-120` 及 `+120` 并分别推进一帧；实际运行时距离均保持 1250。
