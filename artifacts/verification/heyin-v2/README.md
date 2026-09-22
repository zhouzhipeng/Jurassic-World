# 禾音比例与动作修正

日期：2026-09-22。游戏源码版本：`61ff7ce`；本轮基线：`8726524`。此目录仅保存该源码版本的证据，后续证据提交不修改游戏源。

## 修改

- `tools/build_heyin.py`、`sources/models/heyin-source.blend`、`assets/models/heyin.glb`：身体横向比例略增，头部适度放大，保留成年造型。模型三个尺寸等比换算到 192 单位的站立高度；主角 Body 高度为 202 单位。
- `scenes/Game/objects/Heyin.settings`：尺寸按新模型真实包围尺寸设置，保留 keepAspectRatio。运行快照确认 depth 为 192。
- `scenes/Game/external-events/HeyinJourney.events`：待机、交谈、休息互斥，只有动作名变化时才切换，消除每帧先 Idle 再 Talk/Rest 的重启。朝向保留经侧面预览确认的移动方向减 90 度。
- 受伤与休息改为双脚支撑的轻度屈膝站姿，取消原来的悬空深蹲。行走使用烘焙双骨骼解算，支撑脚保持地面高度；24 帧、30 fps 的循环配合 160.68 单位/秒跟随速度。移动速度降低后，护送测试给出相应的步行时间。
- `docs/HEYIN_GAMEPLAY.md` 与 `tools/README.md` 更新当前动作说明和检查入口。

## 验证

`tools/check_heyin_asset.py` 通过 Blender 5.1 后台执行：GLB 重新导入为一个骨架、五个精确命名动作、无缺失外部图片；源文件 19 个姿态采样的支撑脚踝与地面保持一致，网格最低点约 0.001 米。具体数值见 `asset-checks.json`。`walk-pose.png`、`rest-pose.png` 是该模型的 Blender 渲染。

源码通过结构、事件生成、扩展生成、JavaScript 与语义检查，提交后执行 verify_project_change，回执见 `runtime.json`。预览无运行错误，World3D 无失败贴图或拒绝对象。

玩法测试与断言结果见 `gameplay.json`：当前版本重新执行 HeyinJourney 与 HeyinPersistence，覆盖成人尺寸、正确朝向、跟随速度、救助扣料、危险阻挡、等待、暂停、营地护送、休息恢复、清泉线索、建筑阻挡和触屏存读档。未重跑全部历史测试。

## 截图与边界

- `encounter.png`：受伤姿势。
- `side-by-side.png`：主角与禾音在相同地面 Y 坐标的尺度对照和交谈姿势。
- `talk-later.png`：再推进 40 帧后的交谈姿势。
- `walk-a.png`、`walk-b.png`：沿 +X 朝玩家跟随，相隔 24 帧，确认脸部朝向和左右脚交替。对应位置样本在 `runtime.json`。

截图位置、相机、剧情阶段及交谈文字通过调试工具安排，用于视觉核对；输入驱动玩法证据来自两个独立测试。截图缩放为 1600×900，未用其 FPS 数字作性能结论。本轮未改变寻路、战斗或后续剧情范围，未做移动设备实机验收。
