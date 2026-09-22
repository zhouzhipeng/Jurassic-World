# 禾音开篇验收

日期：2026-09-22。游戏源码版本：`c09b2c0`（`Keep companion dialogue clear of survival HUD`）；开发基线：`a8e63b6`。本目录的测试、预览与截图对应该游戏源码版本，后续仅补充验收文档的提交不改变运行源。

## 交付范围

- `docs/HEYIN_STORY.md`：成年女性同伴、迁徙失散原因、六章寻亲、家人、对白、线索和团聚尾声。
- `docs/HEYIN_GAMEPLAY.md`：当前开篇操作、路线、存档与限制。
- `assets/models/heyin.glb`、`sources/models/heyin-source.blend`、`tools/build_heyin.py`：原创角色及可重复制作流程。
- `scenes/Game/objects/Heyin.settings`、`HeyinStory.settings` 和 `external-events/Heyin*.events`：实际 NPC、救助、护送、跟随/等候、疲劳、寻亲线索与存档。

## 模型检查

26,932 三角形，16 根骨骼，12 个材质分组，GLB 831,736 字节。原点在双脚之间，站立高度约 1.71 米，游戏中使用 100 单位/米。支持原始 PBR 材质，无外部图片或 buffer 依赖。

Blender 5.1 后台生成成功；导出的 GLB 重新导入确认一个骨架和五个动作。GDevelop `inspect_glb_model` 确认精确动画名：Idle、Walk、Rest、Talk、Injured。检查了模型正面、侧前方、脸部、行走和休息姿势，裙摆使用腿部混合权重。`walk.png`、`rest.png` 是同一最终模型的 Blender 动作检查，`roundtrip.json` 为重新导入记录。

## 游戏检查

`checks.json` 保存当前版本的结构验证、模型检查和测试摘要。结构、事件代码生成、扩展生成代码、JavaScript 检查、语义检查全部成功。按照项目规范先提交再重载。

测试包含 `tests/HeyinJourney.js`（12 条）、`tests/HeyinPersistence.js`（6 条）、原有 `tests/SurvivalPersistence.js`（11 条）。覆盖：缺材料、附近捕食者、安全救助的准确扣料、等候与跟随、真实动画、暂停、实际护送到营地、疲劳恢复、一起辨认线索、重复交互、房屋阻挡、实际触屏操作、跨场景存读档，以及原生存系统回归。

最终预览使用 `verify_project_change`：1 个禾音实例、有限坐标、零运行错误；World3D 有 Three group 和可见网格，失败贴图与被拒绝对象均为 0。验收回执见 `runtime.json`，截图见 `encounter.png`、`companion.png`。截图中的位置与相机由调试工具安排，救助动作通过真实 G 按键触发；剧情完成证据来自上述输入驱动测试。

## 明确边界

目前是可玩的故事开篇，后续山口、断桥、石脊、白石台地及家人团聚尚未制作。角色使用地面跟随，复杂寻路、入屋、楼梯与骑乘未支持，遇建筑停下并提示玩家绕行；没有永久死亡或战斗 AI。草药生产属于后续设计。

当前版本未重跑全部 38 项历史测试，未做真实手机设备性能测试或竖屏截图验收；不把历史验证视为本版结果。界面的窄屏布局有实现，正式移动端发布前仍需实机检查。
