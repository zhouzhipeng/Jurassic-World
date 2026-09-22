# 营地木屋入口验收

源码版本：`1b4bae038fcb74d3b97397f90afdbe7c7d9e8410`
提交：Allow players to enter the camp house through its doorway
问题：`issues/issue-20260922-010529-658.md`

整屋矩形阻挡改为左右墙、后墙和门口两侧墙体。按现有岛屿模型的坐标与比例保留入口，台阶高度为 10，木地板表面为 30.5。

改动源码：

- `scenes/Game/functions/sceneUpdate.events`：营地木屋墙体碰撞。
- `scenes/Game/external-events/ModularConstruction.events`：台阶与地板支持高度。
- `tests.settings`、`tests/CampHouseEntry.js`：入口回归测试。

验证结果：

- 项目结构、事件生成、扩展代码、JavaScript 和语义校验均通过；校验回执本身仅证明静态有效。
- 提交后 `reload-project-80` 成功重载。
- `gameplay-tests-d5cdef42-53b8-46fe-a8b5-ede22d40f81f`：CampHouseEntry，903 帧，13/13 断言通过，completed / all_passed。
- `gameplay-tests-ab6323eb-73f3-4057-93ff-ec06e61d060b`：PlayerJump，571 帧，12/12 断言通过，completed / all_passed。涵盖四级平台、落地、菜单暂停、触屏跳跃和独立攻击。
- 新暂停预览 `preview-ws-9` 从门外 (-900,-300,0) 按 W 65 帧，到达 (-900,-679.167,30.5)，随后松键站稳。截图已目视检查。
- World3D 渲染层具有 Three 场景、组和相机，298 个可见网格、0 个拒绝对象、0 个失败贴图。

范围：截图所示的固定营地木屋，键盘/摇杆行走、进出、墙体阻挡和地面跳跃回归。未运行全套游戏测试；没有修改模型或天气系统。

[精简工具回执](receipts.json) · [室内站立截图](inside.png)
