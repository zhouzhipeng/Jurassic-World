# External Events 一次性迁移记录

- 源项目提交：`4891e48969347e20baaef3b58d3f9dd5f4f95c63`。
- 格式：5 → 6；外部片段：28。
- 外部文件：84 → 28；包装文件移除：56。
- 全部 41 个事件源的原始字节一致；28 处外部 Link 的文本、顺序和缩进一致。
- 场景、Prefab、Behavior 的业务事件及对象/布局数据未修改；其 settings 仅更新格式标记。
- 下表是迁移前后相同的正文 SHA-256。

| 片段 | SHA-256 |
| --- | --- |
| HUDActionBar | `6c83bf1eaea41b880ad028b5ef599f617dbf69a1f47c28b196e62644afe3ebfe` |
| HUDAudioControls | `f9e37e202802e5ec3a21696bb9a46a245c6ea86d822f64e4f5e9b26684df439e` |
| HUDBootstrap | `8c4aefb668cb54bb1fee2a36e3b1b5d09eca9ef32e8538a098baf7150174941a` |
| HUDBuildPresentation | `4763fd87b3d7118a324b16402988a2fbe47276253538d4cbe0c351b453175709` |
| HUDBuildSelection | `37e89f5a809bd6bf7c58ac8ba79a4dffcc52f7b55206b48d7c62567cedde1349` |
| HUDBuildStatus | `ffcac28ea1a5ff2dd358dc520be9d94426b699e97e30b92747dfd6eebfa8dcbc` |
| HUDChoppingFeedback | `a71412ad19540e32f57a87631f5ed5044761996d43fd126442cc16c6f80e1bfd` |
| HUDConstructionInput | `3934bd5660556923d95b8ef4fb9bb39537191e19c232856a3518130f1ace49ac` |
| HUDDamage | `7f544e49a05e738f6da0708f2ac4c6fb9ccbd8f50c4f93a8a14bb1fafd049a4d` |
| HUDDeath | `78b78be068e2d6922b83dbe74e96dd3e381ffcf594941d3e97ab5e092cd6726a` |
| HUDExplorationHint | `47ad78879680f661be4bb7d905411570bead6809213b4d360fffad68fccc708f` |
| HUDHarvestFeedback | `8b08ba0ca066736aea2bf6bfcd94e3367477a52e3eefb30924df6f8c2dde46e4` |
| HUDHarvestReset | `c3c937ed23ba70591d14536b6f0babc2c69131f2efaade5c9fc0b1dfd2158012` |
| HUDHealth | `38a6614fcd5cb7d41511f103c466582121c81ee178a5ff0dde2bafb710f04f4f` |
| HUDInventoryAndSave | `f15c7e3de33019e6530215c4fbc923e818fbbd386e3dcfeaf7bfa0d798b47876` |
| HUDLoadStatus | `1a20e7859c10326b045eb4510064fc0d86f779dbff540c00dfd721eeec3bfd83` |
| HUDMenuInput | `535b7f9e9f06977f575654541ddd4479b5667b1d6750bf6590db737f3f47a4d8` |
| HUDMountInput | `34fc52db627d5c1918c4fb467a3ae133ad221eda214a899f16ca78b705238281` |
| HUDMountStatus | `fc01f5337dc3997ee304f203b3b488925a3aaf18fb1d99b604d64ef170ff1564` |
| HUDPanels | `b882931cb2936ae8f584fcc699e3129b89be6c5972e5c67e23bf02bac2284674` |
| HUDQuests | `f8f5d0b2c721fae9051efe1271fef31b60443d7230af05c0ff6d73743cadbc37` |
| HUDRaptorHint | `771efebd8f3e9d26fe5e6dfe8f9744b98ebf8141797fb94f86ecb732725bbaff` |
| HUDSaveAvailability | `6f75841cfdeb9e8bb88999fc849bbaf8529e6e5adf58c68007f49e8860385820` |
| HUDStegosaurHint | `eb0a92747d4c9c65e28f647486dd28a56ffe9429a608155bb7eaa0d76fbeb570` |
| HUDTriceratopsHint | `d606cac6b4b207172450bb3a7193915da2aa6ee6adaf4c6bdb9ae1580f058ffc` |
| HUDTyrannosaurHint | `60a225ff652724d3189075f8460a2baf117f1492df1372f9cbbb965a0684c8ea` |
| HUDViewMode | `7505a880fd7aa833b2e855a3c3fca887b5270aea433abbd6ea8daf9ec327c6c5` |
| ModularConstruction | `e2055adac6513f69191ae286f098936c3dd55ddd6f8cde71354622d15c47bcf9` |

## 验证

- GDevelop 新引擎成功打开格式 6 项目。
- `generate_catalogs` 完成；settings catalog 为版本 3，片段只有 eventsUri。
- `validate_project_files`：valid=true；序列化往返、结构、语义检查、场景与扩展代码生成均通过，诊断为零。
- 引擎：Core 138 个断言通过；相关编辑器与存储回归 210 项通过；场景代码生成 10 项通过；生产构建与修改文件 ESLint 通过。
- 存储套件中已有 Physics3D 隐藏属性断言与当前扩展声明不符；使用 HEAD 版本 catalog 生成器复现确认，与本次重构无关。该单项未计入通过数量。
