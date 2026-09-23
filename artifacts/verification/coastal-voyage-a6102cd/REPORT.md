# 近海航行验收

源码修订：`a6102cd48ad9b0b6ac5f24393427cdb534b0418a`（`Restore boat safely after loading and respawning`）。前置功能提交：`3d497d668824c7069613fb9c02a7444947e90af8`（`Add rowboat voyage and explorable nearshore islet`）。

## 范围

- 小船和近海小岛：`assets/environment/coastal-rowboat.glb`、`assets/environment/nearshore-islet.glb`；可编辑制作源位于 `sources/environment/`。
- 场景对象与布局：`scenes/Game/objects/Rowboat.settings`、`scenes/Game/objects/NearshoreIslet.settings`、`scenes/Game/scene.settings`。
- 航行、靠岸、步行和触屏互动：`scenes/Game/external-events/CoastalVoyage.events`、`scenes/Game/functions/sceneUpdate.events`、`scenes/Game/external-events/ModularConstruction.events`、`scenes/Game/external-events/TouchContext.events`、`scenes/Game/external-events/TouchInput.events`。

## 结果

- `validate_project_files`：`valid`、`structurallyValid`、`eventCodeGenerationValid`、`extensionGeneratedCodeValid`、`javascriptAuthoringValid`、`semanticLintPassed` 全为 `true`。
- `verify_project_change`：`runtimeVerified: true`、`completionReady: true`。小船和小岛各 1 个实例，坐标有限；`World3D` 有 345 个可见 mesh，0 个纹理失败、0 个渲染拒绝对象、0 个运行错误。
- 暂停预览按帧操作：玩家从 `(5560,-1000)` 按 F 登船；按 D 航行 100 帧后小船到 `(6883,-1000)`；按 F 登岛，玩家到 `(7183,-1000,25)`。步行深入岛内，东侧边界停在 `x≈8280`，再回到西侧上船并划回主岛，下船后玩家到 `(5452,-901,0)`。
- 触屏交互按钮在船边显示「上船」，命令值为 `311`。在小岛模拟死亡并按 Return 重生后，玩家回到营地 `(-650,350)`，船回到主岛岸边 `(5850,-1000)`。
- [航行画面](underway.png)与[小岛登陆画面](islet-landing.png)来自上述源码修订的新预览。

## 未覆盖

本轮没有执行跨全新预览的海上存档读取或真实触屏点击；只检查了对应恢复逻辑和触屏按钮的运行状态。
