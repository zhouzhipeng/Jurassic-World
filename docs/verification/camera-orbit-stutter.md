# 转镜头卡顿修复

对应问题：`issues/issue-20260921-094307-865.md`。

## 原因与修复

首次转向新的植被时，Three r185 的 WebGL TSL 兼容后端把节点实例标识作为 GPU 程序缓存键。相同着色器、不同透明度参数的植被无法共享程序，首次进入视野时集中编译，产生明显停顿。

修复位于 `D:/code/GDevelop`，提交 `9b0760f443`（Share equivalent TSL GPU programs without sharing uniform bindings）。编译后的节点着色器按完整源码和其余编译参数共享 GPU 程序；每个材质仍保留独立的节点、uniform 和更新状态。普通材质沿用原有路径。已重新构建 Three TSL bundle 和本地编辑器使用的 GDJS runtime。

独立 WebGL 测试在修复前确认 32 个等价材质生成 32 份程序；修复后只生成 1 份。像素读取验证了不同颜色独立、同一材质替换 uniform 节点、不同表达式生成不同程序，以及销毁一个材质后其他材质正常。UBO 单元测试也通过。

## 同机测量

同一 CameraOrbitPerformance 场景，180 帧转一圈，不预先转动相机。帧耗时为测试机执行工作耗时，不能直接等同于所有设备的实际 FPS。

| 测量 | 修复前 | 修复后 |
| --- | ---: | ---: |
| 首圈平均帧耗时 | 16.85 ms | 12.69 ms |
| 首圈最坏帧 | 241.4 ms | 65.4 ms |
| 第二圈平均帧耗时 | 11.77 ms | 11.24 ms |
| 第二圈最坏帧 | 16.7 ms | 17.5 ms |
| 终点三角形 | 157,138 | 157,138 |
| 终点 draw calls | 554 | 554 |

首圈最坏帧降低约 73%，重复编译警告消失。首圈仍有约 65 ms 的首次材质构建峰值，不能宣称每帧稳定 60 FPS。没有降低模型细节、删减物体或关闭相机避障。

## 防回归

项目提交 `929ccb6`（Guard first camera orbit against shader compilation stalls）更新了 `tests/CameraOrbitPerformance.js` 和 `tests/CameraDinosaurPerformance.js`。原测试只对第二圈限制最坏帧，现在第一圈也要求平均 <20 ms、采样 P95 <33.3 ms、最坏 <100 ms。P95 使用 harness 的每两帧最大值桶，是保守指标。修复前的 241 ms 峰值会触发失败。

完整测试操作 ID、断言和性能结果保存在 [verification-camera-orbit-stutter.json](verification-camera-orbit-stutter.json)。这些改进依赖上述引擎提交；仅拷贝游戏项目到未修复的编辑器不会获得缓存修复。
