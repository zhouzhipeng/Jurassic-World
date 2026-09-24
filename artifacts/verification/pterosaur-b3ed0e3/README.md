# 翼龙骑乘与飞行验证

源码修订：`b3ed0e3`（包含 `ffc04b2` 和 `6caf572`）。本目录仅记录该修订的运行结果。

## 范围

- 翼龙、鞍具及骑乘角色模型：`assets/models/pterosaur.glb`、`assets/models/pterosaur-saddle.glb`；可编辑源文件位于 `sources/models/`。
- 骑乘、飞行、相机、触控与存档逻辑：`scenes/Game/`。
- 自动化用例：`tests/PterosaurFlight.js`。

## 结果

- `validate_project_files`：结构、事件代码生成、扩展代码生成、JavaScript 编写规则及语义检查均通过。
- `reload_project`：`reload-project-188` 完成。
- `tests/PterosaurFlight.js`：`gameplay-tests-24f56cb3-1256-430e-b3a6-a8057d3708ea` 完成，15 项断言通过，0 项失败。覆盖鞍具材料消耗、键盘及触控骑乘、升降、水平移动与落地离鞍。
- `verify_project_change`：当前修订的运行检查通过，`runtimeVerified=true`、`completionReady=true`，9 项对象、3D 渲染与运行错误断言均通过。
- 人工检查画面：[飞行截图](flight.png)、[海岸飞行截图](coastal-flight.png)。两张截图均来自该修订的运行预览，分辨率为 3196 × 1800。

存档跨进程恢复及所有地形边界未纳入自动化用例。运行检查仍报告已有的 `ConstructionController` 空自定义对象警告；未报告运行错误。
