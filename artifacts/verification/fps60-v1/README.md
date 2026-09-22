# 60 帧优化验证（2026-09-22）

基线源码：`ebd096f`。最终游戏源码：`7ccca00`。后续文档提交不改变该受测游戏源码。

## 结论

**尚未达到稳定 60 帧。** 相同 `tests/CameraPerformance.js` 营地移动场景的平均帧耗时从 30.82 ms 降到 18.39 ms，减少约 40%。该测试的 33 ms 平均门槛通过，不等于通过 60 帧验收。

严格 `tests/FrameBudget60.js` 使用完整地图、正常 HUD、营地移动/转镜头、围栏移动与山地转镜头，每处预热 90 帧后测量 180 帧。最终结果：

| 场景 | 平均 ms | p95 ms | 最大 ms |
| --- | ---: | ---: | ---: |
| 营地移动 | 19.22 | 24.9 | 80.3 |
| 营地转镜头 | 18.10 | 34.1 | 70.3 |
| 围栏移动 | 13.28 | 18.5 | 20.5 |
| 山地转镜头 | 13.66 | 18.9 | 23.4 |

平均和 p95 均须不超过 16.67 ms，最大值须不超过 33.33 ms；该门槛失败。测试工具按不受帧率限制的方式推进模拟，表中数值是宿主机执行成本，不是正常播放的呈现 FPS。p95 根据工具返回的 frameTimesMs 计算；工具以每 2 帧一个桶返回样本，不能作为逐帧原始分布。参考机器为 Ryzen 9 7900X3D / RTX 5060 Ti，预览画布随桌面窗口尺寸变化，结果不外推到其他设备。

## 修改范围

- `assets/models/island.glb`：269 个 primitive 合并为 24 个，保留 51018 个三角形；三角形位置、法线、UV、材质对应关系经过精确签名比较。`tools/partition_island.py` 支持可选批次上限，默认值仍为 256；山地构建使用 4096。Blender 可编辑源未改动。
- `scenes/Game/external-events/CameraVisibility.events`：保守范围筛选、同帧完整射线结果复用、移动时减少变量树分配。
- HUD 删除重复排布与覆盖后不可见的旧同伴面板工作，样式变化才设置，状态条按 1% 变化重画。
- 浆果/蕨类提前切换 LOD，停止投射小型植被阴影；保留树木、角色、建筑阴影和 MSAA。
- 远离玩家 36 米且远离禾音 18 米的剑龙、迅猛龙、霸王龙暂停活体 AI；对象身份、生命值、死亡和重生计时保留。
- FPS 显示保存同一个真实采样到 `FPSCounter.MeasuredFPS`，没有人为抬高或固定显示值。

## 回归与限制

最终 `7ccca00` 的 CameraPerformance、CameraSmoothFollow、DistanceVisibility 通过，详见 `final-tests.json`。最终结构校验通过，基础运行检查确认无运行时错误、无失败纹理、无被拒绝的 3D 对象且有可见网格；这些检查不替代帧率门槛。

正常播放在 3014×1800 画布上进行 WASD 移动，12 次实时 FPS 采样约 23.7–59.8，多数为 53–60，但明显掉帧仍存在。调试器取样会序列化场景并扰动耗时，因此这些数值仅作诊断；原始值见 `live-verification.json`。`live-camp.png` 已人工检查，HUD、人物、地形正常呈现，截图时显示 40 FPS。采样结束已释放按键并暂停预览。

`pre-cache-tests.json` 对应 `e5428cc`：野生动物激活/重生、植被 LOD、距离显隐、触屏操作、平滑镜头、营地进屋通过。该批次 CameraPerformance 曾出现 `this.object.getZ is not a function`，最终源码独立复测通过；保留该异常记录，不宣称已定位或修复引擎问题。

旧测试 TouchMenus、MountainRadar、CameraVisibility 在隔离的 `ebd096f` 基线也失败，见 `baseline-failures.json`。HeyinSurvival 在旧同伴面板可见断言处失败；基线的 HudPresentation 已隐藏 HeyinVitals，因此该断言不符合当前 HUD，后续生存断言未执行，不计为通过。

`intermediate-results.json` 记录各优化阶段的源码版本与剖析数据。删除岛屿/植被、关闭触控 UI 的诊断场景仅用于定位瓶颈，不作为交付验收。关闭 MSAA 的试验没有明确收益，最终已恢复。

剩余主要成本在营地渲染与事件执行，仍需进一步剖析长帧和密集场景；当前不能保证稳定 60 帧。
