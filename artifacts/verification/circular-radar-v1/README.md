# 圆形雷达验收

源码版本：`7ae5a7211007c8cce34c52767f124a64f20304c1`（Make navigation radar circular）。

修改 `assets/ui/radar-map.svg` 为透明四角的圆形罗盘，保留北向、方位与图例；`scenes/Game/external-events/MapRadar.events` 同步缩放地图标记坐标。`tools/render_radar.py` 可独立重建底图，`tools/build_mountain_island.py` 调用它保持输出一致。

最终结构、事件生成、JavaScript 与语义校验全部通过；提交后重载并运行 Game 场景，verify_project_change 返回 runtimeVerified=true、completionReady=true。雷达实例数、玩家标记有限坐标、运行错误数为零三项断言通过。人工检查 `preview.png`，圆形边框、透明外侧及玩家/营地标记显示正确，未遮挡旁边按钮。本次为外观调整，未重跑整个山地测试集。
