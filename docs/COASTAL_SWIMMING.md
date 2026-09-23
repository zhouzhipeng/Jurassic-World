# 沙滩、游泳与潜水

主岛四周新增连续的干沙、湿沙、浅水与海底坡面，步行可从陆地进入海水。
主岛边线以 X ±6400、Y −6700～6200 为基准，沿岸有弯曲变化；平缓沙滩约 12 米宽，山坡在沙带内侧渐起，海底延伸到近海
活动边界。海平面为 Z −80，入海后随水深切换游泳状态。小岛及划艇仍使用
独立逻辑。

键盘：WASD 游泳，C 潜水，空格上浮。触屏摇杆游泳，水中原「跳跃」按钮
切换为「潜水」或「上浮」。潜水时氧气下降，浮出水面后恢复；耗尽后生命值
下降。近海底部限制潜入深度，返回浅滩恢复步行与跳跃。

可编辑地形源：`sources/environment/island-coast-source.blend`，由
`tools/build_walkable_coast.py` 从保留的山地源生成。可编辑角色源：
`sources/models/survivor-swim-source.blend`，由 `tools/add_swim_animations.py`
从钓鱼版本角色源生成。运行资源分别为 `assets/models/island.glb` 与
`assets/models/survivor-animated.glb`。两个脚本只写指定的临时输出目录；
检查后再安装到工程。岸线高度参数修改时，需同步地形脚本与
`scenes/Game/external-events/MountainActors.events` 的高度表达式。

行为验收：`tests/CoastalSwimming.js`，覆盖沙滩入海、游泳、潜水耗氧、
海底限深、上浮及返回岸边。
