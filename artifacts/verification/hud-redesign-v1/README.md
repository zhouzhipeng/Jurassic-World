# HUD 改版验收

源码版本：`d469e0dfbdfda730cce913df823589bb08cc0a38` — `Hide touch panels behind companion conversations`。

实现包含森林绿半透明面板、实时生存进度条、左侧任务与伙伴状态、顶部时间天气、地图下功能入口、金色主交互按钮及底部交互卡。代码入口与资源归属见 `docs/HUD_DESIGN.md`。

## 当前版本结果

- `validate_project_files`：结构、事件生成、扩展生成代码、JavaScript API、语义检查全部通过。
- `verify_project_change`：`runtimeVerified = true`、`completionReady = true`，运行时错误 0，World3D 贴图失败 0，HUD 对象数量正确。
- `tests/TouchResponsive.js`：24 项断言通过。1600×900、1155.56×650、2133.33×1200 的操作区域、建造按钮、背包格子与标签均在屏幕内，建造工具不重叠。
- `tests/TouchControls.js`：27 项断言通过。多指移动、镜头、攻击、菜单暂停、拖离按钮取消和拖动转镜头均正常。
- 最终预览通过真实 touchStart / touchEnd 点击背包、返回、交谈、结束交谈及救助。救助使 `HeyinStage` 从 1 变成 2，`Rescued = 1`、生命恢复到 100。
- 禾音对话打开时不残留触控菜单标题或背包面板。

机器可读摘要：本目录的 `runtime-verification.json`、`interaction-results.json`。

## 当前源码截图

均为当前源码的原生 canvas 捕获，3196×1800，没有图像重绘。测试安排只改变预览中的玩家位置、时间与生存数值，不改变项目默认值或用户存档。

- [救助前 HUD](near-heyin.png)
- [背包入口](backpack.png)
- [禾音交谈](dialogue.png)
- [救助完成](rescued.png)

## 检查范围与未通过的既有用例

主要验收横屏默认触控 HUD；竖屏、历史桌面参考模式不属于此版视觉验收范围。

`tests/TouchMenus.js` 在中间源码 `cf3aee2` 上未通过首项建造前置断言：它将玩家放在 `(-1780,-135)`，得到 `PlayerFloor = 258.402`，建筑候选位置 `(-1800,-600)` 被当前地形判为山坡。实际入口已使 `BuildMode = 1`、`BuildKind = 10`，但 `BuildValid = 0`，原因是“山坡无法放置平地建筑，请到山谷或营地平地建造”。本任务未改地形或放置规则，也未修改此用例。不能将它报告为通过；其后续建造、合成、存档断言未执行。最终 HUD 的建造入口和按钮布局由上述通过的 TouchResponsive 用例覆盖，背包和同伴交互另有实际点击验证。
