# 项目目录约定

所有路径相对于包含 `project.gdevelop` 的项目根目录。本文约束项目辅助目录；GDevelop 组件结构以项目技能和生成的 catalog 为准。

| 路径 | 用途 | Git 策略 |
| --- | --- | --- |
| `project.gdevelop`、`resources.settings`、`constants.toml` | 项目入口、资源注册、编辑器常量 | 提交 |
| `scenes/`、`extensions/` | 场景、对象、事件、Prefab、行为 | 提交，保持引擎规定的层级 |
| `objects/` | 存在全局对象时由规范结构使用 | 按需生成 |
| `tests.settings`、`tests/*.js` | 测试清单与平铺测试源码 | 提交，禁止嵌套测试目录 |
| `assets/` | 游戏资源及配套资源清单、许可证 | 提交，已注册资源不随意移动 |
| `sources/` | Blender 等可编辑制作源文件 | 提交；`.blend` 沿用 Git LFS |
| `materials/` | TSL 材质源码 | 提交，属于游戏源文件 |
| `tools/` | 资源制作、转换和维护脚本 | 提交，执行前阅读工具说明 |
| `docs/` | 当前开发说明、设计和历史说明 | 提交 |
| `artifacts/verification/<任务或版本>/` | 正式验收报告、同批截图和说明 | 精选后提交 |
| `artifacts/previews/` | 独立展示截图 | 精选后提交 |
| `artifacts/local/`、`tmp/` | 高频生成结果、中间文件 | 忽略；不要将唯一制作源存入其中 |
| `builds/` | 本地导出包 | 忽略，按需创建 |
| `issues/` | 引擎诊断报告、录屏、日志和内存转储 | 已忽略 |
| `.gdevelop/` | 编辑器状态、生成目录和 API 声明 | 已忽略，不手工编辑 |
| `skills/` | 随项目提供的引擎与 Blender 工作流 | 提交 |

## 资源制作

`sources/models/` 保存模型源文件，`sources/environment/` 保存环境源文件。运行用 GLB、贴图、字体、声音保留在 `assets/`；不为了目录整齐而改动资源注册或游戏事件。

现有资源清单保留在原资源目录，其 `file` 简写相对于所在资源目录解析。环境源的 HDR/PNG 输入也保留在 `assets/environment/`，与许可证和导出资源一起管理。新增制作源和导出文件应在工具说明中明确对应关系。

## 验收产物

新验收使用 `artifacts/verification/<任务>-<版本>/`，报告和对应截图放在一起。报告记录源码提交号、验证范围、工具回执、结果和未验证范围；路径使用项目相对路径。Markdown 链接仍按文档所在位置解析。

迁入 `legacy/` 的旧报告保留原有结论和版本信息；缺少提交号的历史记录不补造版本。历史路径已随迁移更新，但这不代表重新运行了当时的验证。后续重新验收应创建新的版本目录。

独立展示截图放 `artifacts/previews/`。本地试验放 `artifacts/local/` 或 `tmp/`；有意保留的结果再迁入正式目录。不要把测试结果放进 `tests/`，不要再创建根目录 `preview/` 或 `docs/verification/`。

## 文档维护

根 README 只维护运行入口、当前操作说明链接和目录入口。功能细节放对应专题，过往阶段说明保留在 `docs/history/` 并标明时效，避免把不同版本的操作混成当前指南。
