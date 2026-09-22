# Gameplay tests

原生 GDevelop 测试覆盖建造、天气、昼夜、生存、触屏、背包和性能等行为。下表保留最初建造测试的详细说明；完整当前清单以 `tests.settings` 为准。清单位于 `tests.settings`，每条测试的独立异步脚本位于 `tests/`。

| 测试 | 覆盖行为 |
| --- | --- |
| ConstructionPlacement | 地基吸附、相邻拼接、准确扣材、重复放置和材料不足时不扣材 |
| ConstructionSupport | 悬空拒绝、上下层同位置墙体、支撑依赖、按楼层拆除、材料返还 |
| ConstructionDoors | 门框要求、关门碰撞、E 开关门、开门通行、开门后插槽仍被占用 |
| ConstructionStairs | 地基和柱子搭建、楼梯连接、洞口保护、上下楼、楼板站立 |
| ConstructionPersistence | 暂停菜单存档、重建场景、菜单读档、建筑位置及高度、支撑关系、开门状态和库存恢复 |

每条测试从 `Game` 的新场景开始，以固定 60 FPS 模拟，所有按键和鼠标输入均在结束时释放。初始库存和玩家位置用于布置测试条件；楼梯场地的浆果灌木设为采集冷却。建筑创建、拆除、开门、行走和存读档均走实际玩家输入路径，没有直接写入预期结果。

存档测试仅使用 `JurassicWorldGameplayTests_Persistence` 测试槽，每次先保存本次搭建结果再读取。不会覆盖 `JurassicWorldDemo` 正常存档。比较有效建筑时保留原始槽位编号，忽略读档预分配的空槽位数量。

## 运行

在 GDevelop 的 Gameplay Tests 界面运行全部测试，或用 MCP：

1. 修改源文件后先运行 `validate_project_files({})`。
2. 检查并提交修改，然后 `reload_project`，等到重载完成。
3. `run_gameplay_tests({"timeout_ms":30000})` 运行全部测试。
4. 使用返回的 `operation_id` 调用 `get_gameplay_test_results`，直到 `status` 为 `completed`，并确认 `summary.all_passed` 为 `true`。

单独运行示例：`run_gameplay_tests({"file":"tests/ConstructionDoors.js","timeout_ms":30000})`。批次执行期间不要重载工程或启动其他预览。

## 引擎前置修复

本次批量测试发现历史按键的释放事件会进入下一条测试，误触发建造快捷键。引擎提交 `275dfbc106` 修复 `InputManager.releaseAllPressedKeys` 仅释放仍按住的键，并在测试收尾时清除释放事件而不推进游戏逻辑。输入管理器及测试运行器的 52 条回归测试全部通过。使用较旧的引擎时需要包含此修复，否则批量测试可能不稳定。

早期建造批次编号、各用例结果和断言数量见 `artifacts/verification/legacy/verification-gameplay-tests.json`。这些测试验证玩法状态，不覆盖画面质量、全部生存系统或性能预算。

## 当前测试清单

清单来自目录整理时的 `tests.settings`，未在本次目录整理中重新执行。新增测试保持 `tests/<名称>.js` 平铺；验证报告放 `artifacts/verification/<任务或版本>/`。

- `tests/ConstructionPlacement.js`：Foundation snapping, adjacent placement, exact costs and rejected placement.
- `tests/ConstructionSupport.js`：Floating rejection, stacked floors, dependent demolition and refunds.
- `tests/ConstructionDoors.js`：Door socket placement, closed collision, E interaction and open traversal.
- `tests/ConstructionStairs.js`：Build stairs, preserve headroom, ascend, stand on an upper floor and descend.
- `tests/ConstructionPersistence.js`：Save and load through the pause menu across a fresh scene using a dedicated test slot.
- `tests/WeatherCycle.js`：Weather cycling, smooth transitions, automatic timer, pause/photo/reference modes, shelter and delayed thunder.
- `tests/WeatherPersistence.js`：Save and restore weather type and timing through the pause menu in an isolated test slot.
- `tests/DayNightCycle.js`：World clock, frame-independent speed, day phases, continuous sunset, midnight, full daily cycle and paused menus.
- `tests/DayNightPersistence.js`：Save and restore day, time, speed and weather together through the native pause menu in an isolated slot.
- `tests/SurvivalSupplies.js`：Verify native survival gameplay, costs, state and input-driven progression.
- `tests/CompanionGathering.js`：Verify native survival gameplay, costs, state and input-driven progression.
- `tests/MetalProgression.js`：Verify native survival gameplay, costs, state and input-driven progression.
- `tests/SurvivalExposure.js`：Verify native survival gameplay, costs, state and input-driven progression.
- `tests/SurvivalPersistence.js`：Verify native survival gameplay, costs, state and input-driven progression.
- `tests/TouchControls.js`：Simultaneous move, camera, attack and menu cancellation.
- `tests/TouchSurvival.js`：One-tap supplies, gathering, cooking and riding.
- `tests/TouchMenus.js`：Touch crafting, construction, quests, navigation and persistence.
- `tests/TouchResponsive.js`：Touch control bounds and card layout at multiple logical resolutions; aspect ratios checked in preview.
- `tests/TouchInventoryGrid.js`：Touch inventory selection, drag cancellation, quantities, food, equipment and crafting.
- `tests/SprintExhaustion.js`：Held Shift and full joystick remain in walk during stamina recovery, then resume running without animation flicker or stacked speed.
- `tests/ConstructionWildlife.js`：Reported adjacent foundation placement, oriented dinosaur clearance, overlap rejection and exact material costs.
- `tests/CameraVisibility.js`：Camera clears walls, hidden blockers, close obstacles and island foliage; restores zoom and follows elevated and mounted targets.
- `tests/CameraSmoothFollow.js`：Reported near-bush view, bounded angle and zoom recovery, foliage restoration and stable follow while moving.
- `tests/CameraTableFollow.js`：Recorded camp table approach keeps a usable view without entering the survivor.
- `tests/CameraWallApproach.js`：Approaching and pressing against the camp wall must not zoom toward a predicted target inside it.
- `tests/CameraFenceFollow.js`：Crossing the camp fence at the reported low viewing angle must not collapse or pump the camera.
- `tests/CameraPerformance.js`：Profile real movement at the reported camp view and fence, with a host-calibrated frame budget and top-center FPS check.
- `tests/CameraOrbitPerformance.js`：Profile first-use and warmed full camera rotations while the player stays still.
- `tests/FoliageLOD.js`：Distance detail selection, hysteresis, near interaction, harvest regrowth and proxy lifecycle.
- `tests/CameraDinosaurPerformance.js`：Reported dinosaur obstruction, animated orbit frame costs and restored camera clearance.
- `tests/PlayerJump.js`：Keyboard and simultaneous touch jumping, four platform landings, side collision, falling, pause and combat separation.
- `tests/PlayerJumpAnimation.js`：Actual child GLB clips, skeletal movement, equipment attachment, pause, apex, contact and locomotion recovery.
- `tests/IdleResponsiveness.js`：Reported platform view stays responsive after prolonged idle, including keyboard and touch input.
- `tests/PlayerOcclusionOutline.js`：Tree and solid obstruction silhouette triggers, clear-view restoration, hidden blockers and original-body animation without a duplicate model.
