# 可编辑制作源

- `models/`：角色、恐龙、道具、建筑和地形的 Blender 源文件。
- `environment/`：海岸天空、海面、近海小岛和划艇的 Blender 源文件。

运行用模型和贴图仍位于 `assets/`。模型制作脚本见 [tools/README.md](../tools/README.md)。制作源参与 Git/LFS 版本管理，不是可删除的缓存。

环境文件依赖的 HDR 与 PNG 保留在 `assets/environment/`；来源及许可见该目录的 LICENSE.md。新增依赖请使用项目内路径或打包进 Blender 文件。
