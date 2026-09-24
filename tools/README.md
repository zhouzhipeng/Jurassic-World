# 项目工具

`build_mountain_island.py`：Blender 5.1 后台执行，`--` 后传入绝对输出目录。
读取 `sources/models/island-expanded-source.blend` 和 `mountain_profile.py`，
仅向指定目录生成山地 GLB、新 `.blend`、雷达底图和核验清单。保留原始模型源，
安装到工程前进行 GLB 往返检查与预览验收。详见 `docs/MOUNTAIN_WORLD.md`。

这些脚本不由游戏运行时加载。路径以项目根目录为基准；普通资源制作脚本仍会写入已有资源，因此运行前应阅读脚本并保存工作。

## Blender 资源制作

`build_walkable_coast.py`：读取保留的山地岛源，重建 12 米宽沙滩与近海海底，
岸边使用 0.5 米网格采样。通过 `-- <绝对临时输出目录>` 生成 `island.glb`、可编辑 blend 和清单。
`build_sand_footprint.py`：通过同样的临时输出参数生成沙滩脚印的可编辑 Blender 源与运行 GLB。
`add_swim_animations.py`：在 `survivor-fishing-source.blend` 后台进程中运行，
通过 `-- <绝对临时输出目录>` 生成俯身交替划臂的 Swim 和双臂前伸的 Dive 动作、角色 GLB、可编辑 blend
和清单。两个脚本不直接覆盖运行资源，检查后才安装到 `assets/` 与 `sources/`。
操作说明见 [沙滩与游泳](../docs/COASTAL_SWIMMING.md)。

使用 Blender 5.1 的独立后台进程运行，脚本路径使用绝对路径：

```powershell
& "D:/Program Files/Blender Foundation/Blender 5.1/blender.exe" --background --python "<项目绝对路径>/tools/build_survival_assets.py"
```

| 脚本 | 输入 | 输出与用途 |
| --- | --- | --- |
| `build_construction_assets.py` | 程序参数 | 旧整栋建筑资源 |
| `build_modular_assets.py` | 程序参数 | 木制模块构件 |
| `build_expanded_island.py` | 程序参数 | 扩展海岛 |
| `build_mount_assets.py` | 程序参数 | 副栉龙和坐姿骑手 |
| `build_player_animation.py` | 程序参数 | 原始八段角色动画；不会包含后续 Jump |
| `build_wildlife.py` | 程序参数 | 四种野生恐龙 |
| `build_spear.py` | 程序参数 | 长矛 |
| `build_survival_assets.py` | 程序参数 | 生存道具 |
| `build_coastal_environment.py` | `assets/environment/` 的 HDR | 海岸天空、海面和天空贴图 |
| `create_coastal_voyage_assets.py` | 无外部输入；Blender 5.1 | `sources/environment/coastal-rowboat-source.blend`、`sources/environment/nearshore-islet-source.blend` 及对应的 `assets/environment/*.glb`；重跑会覆盖这四个文件 |

以上模型脚本的 Blender 源输出已统一为 `sources/models/` 或 `sources/environment/`；GLB、配套清单和贴图仍输出到原 `assets/` 子目录。脚本可重复执行，但会覆盖其输出，且部分脚本代表历史制作阶段，不保证重建当前全部人工修改。此次目录整理没有重新运行这些生成器。

特殊工具：

- `add_player_jump_animation.py`：先加载 `sources/models/survivor-animated-source.blend`，再传入一个临时输出目录；该目录同时产生 `.blend`、GLB 和清单。验收后分别安装到 `sources/models/`、`assets/models/`，不要直接对生产资源目录执行。
- `add_rowboat_seating.py`：分别加载 `sources/models/survivor-jump-source.blend` 和 `sources/environment/coastal-rowboat-source.blend`，通过 `-- character|boat <绝对临时输出目录>` 生成坐姿、划桨与船桨动画的 GLB、可编辑 `.blend` 和清单。仅覆盖指定临时输出目录，检查动画与模型后再安装到现有运行资源路径；可对原始输入重复执行。
- `add_fishing_animations.py`：加载 `sources/models/survivor-rowing-source.blend`，通过 `-- <绝对临时输出目录>` 生成含抛竿、等待、咬钩、收线动作的角色 GLB、可编辑 `.blend` 和动画清单。仅覆盖指定临时目录；检查后分别安装到 `assets/models/` 与 `sources/models/`。重复运行可重建相同动作。
- `build_fishing_rod.py`：使用 Blender 5.1 独立后台进程，通过 `-- <绝对临时输出目录>` 生成鱼竿 GLB 与可编辑 `.blend`。仅覆盖指定临时目录；检查后分别安装到 `assets/models/` 与 `sources/models/`。重复运行可重建相同模型。
- `partition_island.py`：显式传入输入 GLB 和临时输出 GLB，保持原模型供比较。
- `generate_foliage_lods.py`：传入项目绝对路径，读取原植被 GLB，写入 `assets/models/` 的 LOD GLB。

```powershell
& "<Blender绝对路径>" --background "<项目绝对路径>/sources/models/survivor-animated-source.blend" --python "<项目绝对路径>/tools/add_player_jump_animation.py" -- "<项目绝对路径>/tmp/jump-review"
& "<Blender绝对路径>" --background --python "<项目绝对路径>/tools/partition_island.py" -- "<输入GLB绝对路径>" "<临时输出GLB绝对路径>"
& "<Blender绝对路径>" --background --python "<项目绝对路径>/tools/generate_foliage_lods.py" -- "<项目绝对路径>"
```

## 音频制作

`build_heyin.py`：原创禾音角色，使用 Blender 5.1 后台进程，参数 `-- <绝对输出目录>`；生成 `heyin.glb`、`heyin-source.blend`、模型清单及两张展示图，仅覆盖指定目录中的同名产物。先输出到 `tmp/heyin/` 检查，再将 GLB/清单安装到 `assets/models/`，源文件到 `sources/models/`，展示图到 `artifacts/previews/`。可重复制作，不修改已打开的 Blender 会话。

`compose_audio.py` 使用 Python、NumPy 合成音乐和音效，`compose_weather_audio.py` 合成天气声音；均输出到 `assets/audio/`，前者同时更新音频清单。以 Python 运行对应绝对脚本路径即可。设计见 `docs/AUDIO-DESIGN.md`。

## 历史工程修改脚本

`author_*.py`、`setup_*.py`、`add_mount_events.py` 和 `refine_modular_construction.py` 是特定历史版本的工程修改脚本，会写入 `.settings`、`.events` 或资源表。它们不属于资源重建流水线，不应批量执行；部分已有旧版本保护检查。保留原位置便于追溯，不将它们当作当前工程的初始化入口。

编辑当前游戏应遵守 `skills/gdevelop-project-files/SKILL.md`。新增工具应声明用途、依赖、输入、输出、覆盖范围及是否支持重复执行；临时输出统一到 `tmp/`。

`build_camera_bounds.py`：通过 Blender 后台执行，参数 `-- <绝对输出 JSON 路径>`。只读山地 blend，排除规则地面网格，输出各连通景物部件的相机包围盒；可重复运行，仅覆盖指定 JSON。将输出写入 `tmp/`，核对后用 `boxes` 数组更新 `constants.toml` 的 `camera.sceneryBounds`，再校验与验收。详见 `docs/WORLD_PERFORMANCE.md`。

`check_heyin_asset.py`：通过 Blender 后台运行，参数 `-- <绝对模型目录> <绝对报告目录>`，读取该目录的 `heyin.glb` 与 `heyin-source.blend`，检查五个动作、骨架、贴图依赖和 19 个姿态的脚部支撑，输出 JSON 与姿态渲染，不改模型。
