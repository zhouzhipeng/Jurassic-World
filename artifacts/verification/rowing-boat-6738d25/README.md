# 放大划艇与乘船动画验收

- 源码版本：`6738d25df0f4e4f639a3e2e2619731669d511964`（含模型和坐姿动画提交 `886a63f6a1416ab2482ead2bedac38d0bd098a06`）。
- 模型和源码范围：`assets/environment/coastal-rowboat.glb`、`assets/models/survivor-animated.glb`、`sources/environment/coastal-rowboat-rowing-source.blend`、`sources/models/survivor-rowing-source.blend`、`tools/add_rowboat_seating.py`、`scenes/Game/objects/Rowboat.settings`、`scenes/Game/scene.settings`、`scenes/Game/external-events/CoastalVoyage.events`、`scenes/Game/external-events/TouchContext.events`、`scenes/Game/functions/sceneUpdate.events`、`extensions/JurassicActors/prefabs/Survivor/objects/Body.settings`、`extensions/JurassicActors/prefabs/Survivor/functions/doStepPostEvents.events`。
- 船模型显示尺寸从 `220×540×110` 调整为 `286×702×143`，各维增加 30%。Blender 导出的船 GLB 含 `OarsRest`、`OarsRow`，角色 GLB 含 `BoatSit`、`BoatRow`，原有 12 段角色动画保留。GLB 检查：船 9 个网格、角色 7 个网格和 16 根骨骼。
- 项目文件校验：`valid=true`，结构、事件代码、扩展代码及语义检查通过。提交后新预览 `verify_project_change`：`runtimeVerified=true`、`completionReady=true`，运行错误 0，可见 3D 网格 345 个，贴图失败和拒绝对象均为 0。
- 运行验证：小船初始位于 `(6460,-1000,-50)` 的水上；岸边角色 `(5750,-1000)` 可按 F 上船。静止时角色的 `AnimationState=12`、坐姿可见；航行时 `AnimationState=13`、角色与船桨划动。船驶至小岛西侧 `(8681.67,-1000)` 后可下船，角色回到站姿并登岛；再上船返航，于主岛船位 `(6485.83,-901.41)` 下船，角色回到 `(5765.83,-901.41,0)`。
- 画面复核：[水上初始船位](offshore-start.png)、[上船坐姿](seated.png)、[海上划桨](rowing.png)、[小岛靠岸](islet-approach.png)。截图均取自该源码版本的新预览，画布尺寸 3196×1800，质量检查无异常。
