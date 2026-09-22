# 山地、五倍地图与雷达验收

源码版本：`3feb0766a22f4e93b0ee81ba40e7c56be3bfa437`（Verify companion status bounds for compact mountain HUD）。本目录是该源码版本的验收证据。

可探索面积扩大为原来的 5.0002 倍；新增山脊、高地、丘陵与山谷，恐龙由 5 只增加到 25 只。新增 82 处普通资源；泉水总数 6，矿脉总数 12。雷达固定北向，显示玩家位置与朝向、营地和当前导航目标。

主要源码：`tools/mountain_profile.py`、`tools/build_mountain_island.py`、`scenes/Game/external-events/MountainInitialize.events`、`scenes/Game/external-events/MountainActors.events`、`scenes/Game/external-events/MountainFoliage.events`、`scenes/Game/external-events/MapRadar.events`、`scenes/Game/functions/sceneUpdate.events`。模型为 `assets/models/island.glb`；可编辑源为 `sources/environment/island-mountain-source.blend`。功能与重建说明见 `docs/MOUNTAIN_WORLD.md`。

最终校验、源码提交、编辑器重载和运行验证均完成。运行验证 9 项断言通过，运行错误 0、World3D 纹理加载失败 0、拒绝对象 0。`tests/MountainRadar.js` 的 22 项断言全部通过；`tests/HeyinCompanionUI.js` 的 10 项断言全部通过。完整断言见 `results.json`。

在五个位置对实际模型进行射线高度比对，最大高度误差 2.685 游戏单位（约 2.7 厘米）；验证实际爬坡输入、跳跃落地、骑乘高度及跨越旧地图边界。雷达通过桌面 1600×900 与窄屏约 569×320 的显示及按钮避让检查。请求 720×900 时项目自动适配成 1600×900，不作为实际竖屏验收。

截图：`camp.png` 为营地；`highlands.png` 为北部高地俯瞰。两张均来自当前源码运行预览。高地截图使用测试注入位置和镜头，实际移动另由测试覆盖。

限制：网格建筑仍要求平坦山谷或营地，未添加斜坡地基；未作持续帧率保证。Blender 导出模型共 51018 三角形、269 个分块，导入回读已通过。
