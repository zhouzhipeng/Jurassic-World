# 首访剧情序幕验收

源码修订：`546c690`（`Reserve distinct mode for narrated intro`）。路径均相对于项目根目录。

## 范围

- `scenes/Game/functions/sceneLoad.events` 在 `JurassicWorldDemo/IntroSeen` 不存在时进入序幕状态。
- `scenes/Game/functions/sceneUpdate.events` 在用户手势后播放四段 `assets/audio/intro/` 中文配音，并同步更新字幕；播放完成或按 `Esc` 后记录已观看状态。
- `scenes/Game/scene.settings`、`scenes/Game/objects/Intro*.settings` 和 `assets/ui/intro-island.svg` 构成独立开场画面。

## 验证

- `validate_project_files`：`valid=true`，结构、事件代码生成、扩展生成、JavaScript 作者检查和语义检查均通过。
- `reload_project`：`reload-project-486` 完成。
- 暂停预览：序幕图层显示正常；点击后 `intro-1.wav` 在通道 42 播放。分段推进时观察到 `intro-2.wav`、`intro-3.wav`、`intro-4.wav`，字幕画面与段落对应。
- 完整播放后运行时状态 `Mode=0`、`IntroStep=5`，无运行时错误。按 `Esc` 跳过也得到相同状态，未进入旧菜单。
- 再次启动新预览并推进两帧，状态为 `Mode=0`、`IntroStep=5`，开场没有重复播放。

截图：[开始画面](start.png)、[第二段字幕](second-line.png)、[跳过后游戏画面](skip-to-game.png)。

首访启动画面在先前预览中从无 `IntroSeen` 的存储状态直接观察到；最终修订使用隔离的序幕状态值，在调试预览中注入相同状态复核显示、配音、跳过和完整播放。未重新清除本机存档来复验最终修订的空存储分支。
