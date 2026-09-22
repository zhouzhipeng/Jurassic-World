# 室内掉帧修复

问题：`issues/issue-20260922-011715-460.md`
基线源码：`bd0fe34`（仅新增性能回归测试）
验收源码：`caed4378cf7842129356fafdeae32465760ef18b`
实现提交：`3191052` — Stop camera pitch probes once a candidate cannot improve clearance

报告位置为 (-1000.282,-769.460,30.5)，镜头 yaw=20.162602、pitch=23.825573、distance=1250。基线在室内走动时复现失败：平均 41.26 ms，事件占 31.40 ms，渲染占 8.12 ms。

修改 `scenes/Game/external-events/CameraVisibility.events` 的候选仰角搜索：先计算中央头部射线；后续射线只能降低候选净空，因此净空上界已经无法超过当前最佳值加 20 时提前返回。提前返回的上界不会写入精确净空缓存；实际镜头、预测位置及有机会胜出的候选仍完整计算。保留所有原有遮挡分类和镜头平滑规则。

`tests/CampHousePerformance.js` 与 `tests.settings` 添加报告位置的静止、WASD 走动、首次及预热后旋转测试。原测试在移动预算处失败，因此没有基线旋转数据。首次修复运行的首次旋转 p95=48.9 ms，尖峰主要在渲染阶段；最终测试分别保留首次旋转预算（平均 <33.3、p95 <66.7 ms）与预热预算（平均 <25、p95 <40 ms），不隐藏首次帧。

同机、相同画质、确定性测试测量：

| 场景 | 基线平均 ms | 最终平均 ms | 最终 p95 ms | 最终最大 ms |
| --- | ---: | ---: | ---: | ---: |
| 静止 | 17.16 | 11.78 | 14.6 | 16.1 |
| 室内走动 | 41.26 | 24.43 | 38.0 | 56.3 |
| 首次旋转 | 未测 | 23.03 | 45.1 | 113.7 |
| 预热后旋转 | 未测 | 21.46 | 27.1 | 33.2 |

走动平均帧耗时降低 40.8%，事件耗时从 31.40 降到 16.57 ms。首次旋转仍有渲染尖峰；这些是开发机性能采样，不是所有设备的 FPS 保证。

项目所有静态校验阶段通过，提交后 `reload-project-107` 成功。最终 CampHousePerformance 12 项断言通过。CameraVisibility 141 项断言通过，覆盖新墙、隐藏障碍、近墙抬升、恢复缩放、骑乘高度和岛屿旋转视线。CampHouseEntry 13 项断言通过，保留键盘、触屏进出、墙体和地板行为。详细测量见 [performance.json](performance.json)，回归结果见 [verification.json](verification.json)。

最终 verify_project_change 返回 success、runtimeVerified、completionReady 均为 true，零运行错误，World3D 可见网格、Three 组、零失败贴图和零拒绝对象均通过。随后在新暂停预览 preview-ws-11 重现报告位置并推进 180 帧；[截图](inside.png) 已目视检查，室内角色和镜头正常。截图中的 FPS 来自无节奏推进，不能当作实际帧率。

未运行全部游戏测试。模型、阴影、抗锯齿和分辨率设置没有改动。
