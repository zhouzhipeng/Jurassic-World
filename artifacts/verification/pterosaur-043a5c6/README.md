# 翼龙平滑升降验证

源码修订：`043a5c6`。

- `validate_project_files`：结构、事件与扩展代码生成、JavaScript 编写规则、语义检查均通过。
- `reload_project`：`reload-project-207` 完成。
- `tests/PterosaurFlight.js`：`gameplay-tests-9820af28-7e7c-4eef-8779-06424a5e0544` 完成，21 项断言通过，0 项失败，0 项运行错误。覆盖键盘和触控按住升降、首帧无高度跳变、松开后停止、着陆与离鞍。
- 已有的 `ConstructionController` 空自定义对象警告仍存在，不影响本用例通过。
