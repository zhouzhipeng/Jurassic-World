# 序幕启动修复验收

源码修订：`2a02a2b`。下列源码路径相对于项目根目录。

原因：前次验收在本机 `JurassicWorldDemo/IntroSeen` 写入已观看标记，导致同一环境中的后续启动按设计跳过序幕。`scenes/Game/functions/sceneLoad.events` 和 `scenes/Game/functions/sceneUpdate.events` 现使用新的 `IntroSeenV2` 标记。

验证：`validate_project_files` 的结构、事件生成和语义检查均通过；`reload-project-516` 完成。重新启动暂停预览并推进两帧，运行时状态为 `Mode=11`、`IntroStep=0`，无运行时错误，[启动画面](startup.png)正确显示。验证停在开始提示，没有写入 `IntroSeenV2`。
