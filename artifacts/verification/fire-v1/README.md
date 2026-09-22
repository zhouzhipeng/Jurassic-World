# 动态营火验收

日期：2026-09-22。运行源码版本 `8fde6ea`（Animate campfire flames and emit rising 3D embers），基线 `5266fbf`。后续证据与文档索引提交不改变游戏运行源。

## 范围

现有营火模型增加持续形变与轻微摇摆，火星为 World3D 中随机升起、漂移、变暗和缩小的 3D 粒子。使用原生 IfDo、既有火焰 GLB 与简单方块，无额外插件。营地和建造篝火统一生效。最多 96 个火星，远于 1800 单位不发射。燃料耗尽停止发射，余烬在最多 1.65 秒后清理；暂停冻结，加载存档删除旧粒子。

变更来源：`scenes/Game/objects/FireGlow.settings`、`FireEmber.settings`、`scenes/Game/external-events/FireParticles.events`、`SurvivalRestoreWorld.events`、`scenes/Game/functions/sceneUpdate.events`、`tests/FireParticles.js`、`tests.settings`。操作与维护说明见 `docs/FIRE_EFFECTS.md`。

## 验证

结构、事件生成、扩展生成、JavaScript、语义检查均通过。提交后 verify_project_change 重新加载并启动新预览：有一个营火火焰实例，无运行错误，World3D 贴图失败与拒绝对象均为零。

`tests/FireParticles.js` 的 11 条断言覆盖真实 V 键加柴、熄火、粒子上升和缩小、火苗形变、暂停、重新点燃、多个建造篝火、高处营火、96 上限和移除营火后的清理。另回归 `tests/SurvivalSupplies.js`。最终回执与断言见 `checks.json`。

`fire.png` 与 `fire.gif` 来自当前源码的新预览；相机及玩家位置通过调试工具安排，使用 V 键加柴。GIF 是每 5 个模拟帧截取一次的 20 帧游戏画面，裁切放大营火区域，以每帧 83 毫秒播放，未经火焰合成。画面帧率显示不作为性能验收；本轮没有跑全套历史测试或真实手机性能测试。
