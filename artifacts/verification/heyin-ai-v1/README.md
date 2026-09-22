# 禾音专用 prefab AI 验收

日期：2026-09-22。游戏源码版本：`2e2e559`，迁移提交：`20e973d`，本轮基线：`cf85fdf`。本目录证据提交不改变游戏源码。

## 修改范围

- `extensions/JurassicActors/prefabs/Heyin/`：Body 模型封装、onCreated 初始化，以及 UpdateAI 实例状态机。复用现有 Idle/Walk/Rest/Talk 动作，没有修改 GLB。
- `scenes/Game/objects/Heyin.settings`：使用专用 prefab，保留原场景实例 UUID、位置、192 单位模型高度和资源。
- `scenes/Game/external-events/HeyinJourney.events`：保留剧情与输入适配，原跟随、碰撞、体力、动画逻辑迁入 prefab；删除过时场景运动变量。显示和存读档改用实例状态，存档键兼容旧版。
- `docs/HEYIN_GAMEPLAY.md`：当前使用方式和组件边界。

默认 Idle，不再强制 Injured。安全步行靠近 230 单位后自动 Talk，按 180 度/秒转向玩家；超过 280 单位才退出。动画切换互斥，0.2 秒淡化，仅更换动作时切换。原有跟随、障碍停步和体力休息保留。

## 当前版本结果

`results.json` 保存当前版本回执摘要：结构、事件代码生成、扩展生成、JavaScript 与语义检查通过；提交后重新加载并运行 fresh preview。verify_project_change 返回 runtimeVerified 和 completionReady 均为 true，无运行错误，World3D 拒绝对象为 0。

三份测试都在最终游戏源码上重新执行，均 completed 且 all_passed=true，共 36 项断言：

- `tests/HeyinAI.js`：16 项，Idle/Talk 连续播放、救助前自动交谈、限速转身、围绕玩家转向、230/280 距离缓冲、暂停续播、两个实例状态隔离、删除与重新进入场景。
- `tests/HeyinJourney.js`：14 项，材料、危险、救助、跟随速度/朝向、等待、暂停、实际护送至营地、疲劳恢复、清泉线索、建筑阻挡。
- `tests/HeyinPersistence.js`：6 项，实际触屏救助、菜单存档、新场景读档、体力/等候/位置/朝向恢复。

## 画面

- [idle.png](idle.png)：玩家离开后恢复站立待机。
- [talk.png](talk.png)：玩家接近后转身并交谈。
- [talk-later.png](talk-later.png)：交谈再推进 35 帧，手部动作继续变化。

截图为当前源码新预览的游戏画布，1600×900；位置和相机通过调试工具安排。AI 行为另由上述确定性测试核验。截图中的 FPS 不作为性能测量。

本次未重跑全部历史测试，也未验证移动设备实机。原有地面直线跟随、建筑阻挡停步限制保留，尚无完整导航寻路；剧情仍只有一个禾音，额外故事角色需要各自的剧情和存档标识。
