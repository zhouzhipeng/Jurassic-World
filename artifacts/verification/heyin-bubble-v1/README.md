# 禾音头顶对白气泡

日期：2026-09-22。源码版本：`8fbe962`；基线：`90270ae`。此证据提交不改动游戏源码。

`extensions/JurassicActors/prefabs/Heyin/functions/UpdateDialogue.events` 负责头顶投影、圆角背景、小尾巴和文字排版；场景传入世界相机基向量及当前对白。`scenes/Game/external-events/HeyinBubble.events` 负责故事文本与显示条件。两种 2D UI 对象位于 Performance 层，保持屏幕字号。原 HeyinStory 继续显示任务目标，对白移至头顶气泡。

当前源码通过结构、事件生成、扩展生成及语义检查，提交后重新加载，verify_project_change 返回 runtimeVerified=true、completionReady=true，运行错误为 0。

`tests/HeyinBubble.js` 12 项断言、`tests/HeyinAI.js` 16 项断言全部通过，结果见 `results.json`。覆盖靠近显示、对白内容、头顶投影、相机旋转/缩放、长对白背景自适应、提示结束后的交谈文本、菜单隐藏、568×320 窄屏横向边缘约束、离开隐藏及原有 AI 行为。未重跑全部历史玩法测试，未进行移动设备实机验收。

[dialogue.png](dialogue.png) 是同一源码版本的新预览画布，1600×900，位置和相机通过调试工具设置；已视觉核对气泡位于头顶、文字有内边距、小尾巴和圆角底板正确显示。截图中的 FPS 不作性能结论。UI 气泡不进行建筑遮挡射线检测，头顶投影离开视野或距离超过 650 单位时隐藏。
