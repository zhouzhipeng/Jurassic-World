# 静置后掉帧、操作失去响应

对应报告：`issues/issue-20260921-135045-743.md`。

故障发生时角色未死亡、未暂停，输入没有被菜单锁住，场景对象数量正常。按报告中的玩家位置 `(1054.63, 388.13, 90)`、镜头 yaw `176.910569`、pitch `29.501848`、distance `500` 复现。

## 根因与修复

自动天气转换连续修改雾的距离和颜色。引擎的 LinearFog/ExponentialFog 每次数值变化都调用 `TSLMaterialSystem.invalidateSceneInputs`，强制重建植被材质，导致持续渲染卡顿。Three 的 TSL 雾节点本已通过 reference uniform 读取同一个 fog 对象，无需为数值变化重建材质。

引擎提交 `fc3f4fb511`（Update animated fog uniforms without rebuilding TSL materials）移除了数值变化和网络同步时的材质失效通知；启用、禁用及替换雾时仍重建。保留 fog 和 color 对象身份，颜色、距离、密度以及世界缩放继续更新。实际 WebGL 像素测试还发现并修复了 r185 兼容后端缺少指数雾 `fogDensity` 占位 uniform 的错误。

已重新构建 Three bundle 和本地编辑器使用的 GDJS runtime。该修复属于 `D:/code/GDevelop` 引擎，项目复制到其他编辑器时也需要相同引擎修复。

## 验证

天气回归 `WeatherCycle` 全部通过（`idle-weather-after.json`）：降雨、雷暴、雾天、自动转换、暂停、摄影模式及屋顶遮雨维持原有行为。

最终 `verify_project_change` 通过，`runtimeVerified=true`、`completionReady=true`；运行时错误 0，World3D 可见 mesh 296，纹理失败与拒绝对象均为 0。断言摘要见 `idle-preview-acceptance.json`。

- 更新后的两项雾效测试在修复前均失败，修复后通过。
- 雾效与 TSL 材质生命周期专项测试共 30 项通过。
- 真实 WebGL 像素测试验证线性和指数雾连续 120 帧更新距离/密度、改变颜色，画面相应变化，程序数量和材质版本保持不变；已有 uniform 独立性、程序共享和释放测试继续通过。
- 新增 `tests/IdleResponsiveness.js`：90 秒静置分段性能测量，随后用真实按键跳跃、移动，并点击触屏菜单及继续。

修复前：前三段 15 秒窗口平均分别为 11.62、10.75、10.69 ms；覆盖天气转换的第四段升到 106.73 ms，最坏 988 ms，渲染占平均 98.62 ms。回归测试在这段明确失败。原始结果见 `idle-responsiveness-before.json`。测量为本机每帧执行耗时，不等同于所有设备的实际 FPS。

修复后同一测试全部通过：六段平均耗时分别为 11.17、9.98、9.68、9.77、9.92、9.85 ms。原故障窗口降至平均 9.77 ms、最坏 23.3 ms；最后两段最坏分别 16.8、14.9 ms。90 秒静置后的键盘跳跃、移动、触屏菜单打开和继续均通过。初始窗口仍有一次 268 ms 峰值，因此不宣称全程每帧稳定 60 FPS。结果见 `idle-responsiveness-after.json`，操作 `gameplay-tests-8b83f470-12b0-4dee-9b7e-643ad4ab4774`，`completed` 且 `all_passed=true`。
