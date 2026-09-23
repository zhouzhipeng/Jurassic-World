# 沙滩、游泳与潜水

主岛四周新增连续的干沙、湿沙、浅水与海底坡面，步行可从陆地进入海水。
主岛边线以 X ±6400、Y −6700～6200 为基准，沿岸有弯曲变化；平缓沙滩约 12 米宽，山坡在沙带内侧渐起，海底延伸到近海
活动边界。海平面为 Z −80；浅水可涉行，海底低于 Z −160（约 0.8 米水深）时切换游泳，
回到高于 Z −130 的浅滩时恢复步行。小岛及划艇仍使用
独立逻辑。

键盘：WASD 游泳，C 潜水，空格上浮。触屏摇杆游泳，水中原「跳跃」按钮
切换为「潜水」或「上浮」。潜水时氧气下降，浮出水面后恢复；耗尽后生命值
下降。近海底部限制潜入深度，返回浅滩恢复步行与跳跃。

潜水时第三人称镜头降到海面以下，视角转为近距离的水平观察；海面从水下观看时
降低遮挡，玩家可看到海底坡面。上浮后镜头恢复通常的水面视角。

游泳动作由同一角色骨架中的 `Swim` 和 `Dive` 循环片段驱动：水面采用俯身交替
划臂和轻幅打腿，潜水采用双臂前伸的水下划动。动作源保存在
`sources/models/survivor-swim-source.blend`，可用 `tools/add_swim_animations.py`
从 `sources/models/survivor-fishing-source.blend` 重新生成。

可编辑地形源：`sources/environment/island-coast-source.blend`，由
`tools/build_walkable_coast.py` 从保留的山地源生成。可编辑角色源：
`sources/models/survivor-swim-source.blend`，由 `tools/add_swim_animations.py`
从钓鱼版本角色源生成。运行资源分别为 `assets/models/island.glb` 与
`assets/models/survivor-animated.glb`。两个脚本只写指定的临时输出目录；
检查后再安装到工程。岸线及地面高度统一定义于 `tools/mountain_profile.py`；
修改参数后须同步 `MountainActors.events`、`MountainInitialize.events` 和
`MountainFoliage.events` 中的原生高度表达式。

行为验收：`tests/CoastalSwimming.js`，覆盖沙滩入海、游泳、潜水耗氧、
海底限深、水下与水面镜头高度、上浮及返回岸边。
