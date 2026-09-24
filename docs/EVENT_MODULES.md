# Game 事件模块边界

模块索引由引擎生成在 `.gdevelop/project-module-map.json`。定位逻辑时先读该文件的 `linkedFrom`、`links` 与 `eventsPath`，再读对应事件源。新增或拆分片段后运行 `generate_catalogs`；不要手工维护索引。

| 领域 | 场景入口与职责 |
| --- | --- |
| 时间 | `TimeSystem` 更新日历与太阳状态；`TimePresentation` 写入世界状态和 HUD。 |
| 天气 | `WeatherSystem` 更新天气状态；`WeatherPresentation` 处理遮雨、天空、雨幕和声音。 |
| 航行 | `CoastalVoyage` 处理登船/靠岸；`CoastalBoatMovement` 处理位移和划船动作；`CoastalIslet` 处理小岛边界、探索和恢复位置。 |
| 钓鱼 | `FishingLogic` 处理抛竿、咬钩、收线和冷却；`FishingAnimation` 处理人物动作；`FishingPresentation` 处理 HUD。 |
| 生存 | `SurvivalSimulation` 更新人物需求与伤害；`SurvivalFireSimulation` 更新火堆与烹饪；`SurvivalSmelting` 更新熔炼；`SurvivalDeath` 处理死亡。 |
| 任务 | `QuestProgress` 处理进度和领奖；`QuestTargeting` 选择目标并计算方向；`HUDQuests` 呈现任务指引。 |
| 相机 | `CameraActorBounds` 计算恐龙可见范围；`CameraOcclusion` 解决遮挡与轨道；`CameraVisibility` 处理植被淡出。 |
| 建造 | `JurassicConstruction` 扩展拥有建造对象、规则和存档；场景通过 signal 交换命令与结果。详见 `CONSTRUCTION_EXTENSION.md`。 |

上述 Game 片段只服务当前场景，因此保留在 `scenes/Game/external-events/`。对象自身的可复用状态与规则应归 Behavior 或 Prefab；有明确输入输出、可跨场景复用的操作归 Extension Function。扩展与场景之间交换状态或命令时使用 signal，场景保留输入映射、HUD 和场景专属演出。

`sceneUpdate.events` 的 Link 顺序是运行顺序，不应按文件名排序。存档兼容依赖既有变量名和恢复顺序；拆分事件时保留原事件内容与执行次序。
