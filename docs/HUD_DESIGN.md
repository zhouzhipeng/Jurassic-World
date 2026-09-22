# 森林主题 HUD

按确认的效果图实现当前默认触控 HUD（`TouchMode = 1`）。界面仍为原生 GDevelop 对象与事件，图标和面板为 `assets/ui/hud-*.svg` 矢量资源。

- 左上：生命、饥饿、水分、体力；进度条读取实际游戏数值。
- 左侧：可点击的任务卡、目标距离、禾音生命与体力卡。
- 顶部：日期、时间、天气；右上保留真实地形小地图和玩家方向。
- 右侧：菜单、背包、建造、补给；底部保留跳跃、攻击和上下文交互。
- 底部：当前交互说明、救助所需材料、可用时的禾音交谈入口。护送与危险提示按实际状态更新。
- 建造模式：底部右侧使用三行工具按钮，避免与右上入口重叠。

`scenes/Game/external-events/HudLayout.events` 在触控输入前计算布局，调整现有 `TouchButton` 的真实点击区域；`HudPresentation.events` 在场景更新末尾完成文本、进度条和显示状态。菜单命令、多指控制、按住攻击及拖动取消仍由既有触控事件处理。

新增对象定义位于 `scenes/Game/objects/Hud*.settings`，实例归属 `scenes/Game/external-layout/GameTouch.settings`，由现有 HUDBootstrap 创建。字体沿用项目 `interface.ttf`。更换按钮动画后再设置宽高，防止不同贴图原始尺寸造成挤压。

HUD 以 1600×900 为设计基准，按视口等比缩放。主要验收范围为横屏；历史桌面参考模式（`TouchMode = 0`）仍使用原有面板。
