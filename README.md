# 侏罗纪世界 — GDevelop 游戏原型

用支持本项目格式 6 的 GDevelop 打开 `project.gdevelop`，运行 `Game` 场景。当前界面以手机触屏为主，电脑可用鼠标点击界面；移动、视角、采集、建造、背包和存档操作见 [生存与操作指南](docs/SURVIVAL.md)。

项目包含海岛探索、恐龙与骑乘、资源采集、制作建造、生存任务、天气昼夜和海岸环境。历史阶段说明见 [开发记录](docs/history/DEVELOPMENT_NOTES.md)，不作为当前操作指南。

## 开发入口

- [目录约定](docs/PROJECT_STRUCTURE.md)：游戏源文件、资源、制作源和验收产物的边界。
- [开发文档](docs/README.md)：功能、性能、测试与环境说明。
- [资源制作工具](tools/README.md)：脚本用途、输入输出和历史工具限制。
- [资源来源](docs/ASSET_SOURCES.md)：素材来源与已有许可记录。
- [玩法测试](docs/GAMEPLAY_TESTS.md)：测试清单和执行方式。
- [验收产物](artifacts/README.md)：历史验证报告与截图。

## 文件入口

`project.gdevelop` 是项目入口，`resources.settings` 注册资源，`constants.toml` 保存编辑器常量。场景与事件位于 `scenes/`，角色 Prefab 位于 `extensions/`，玩法测试位于平铺的 `tests/`，TSL 材质位于 `materials/`。

游戏资源保留在 `assets/`，Blender 制作源保存在 `sources/`，脚本保存在 `tools/`。正式验收结果放 `artifacts/verification/`，独立截图放 `artifacts/previews/`；`tmp/`、`builds/`、`artifacts/local/` 是本地忽略目录，按需创建。

修改项目须遵守 [GDevelop 工作流](skills/gdevelop-project-files/SKILL.md)；制作模型还须遵守 [Blender 工作流](skills/blender-workflow/SKILL.md)。验证报告只代表其记录的版本。工程依赖的引擎修复见相关环境、性能与历史验收说明。
