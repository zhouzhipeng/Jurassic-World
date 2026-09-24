# 西山矿洞

主岛西侧小山的东坡设有可步行进入的岩洞，入口约在 `(-1750, 600)`，通道沿既有地形升至 `(-2370, 600)`。洞体、木支架、照明、矿脉、水晶和洞穴生物均使用独立 3D 模型；地面仍由主岛原有高度函数支撑玩家，不修改主岛网格或地形公式。

洞内有四处稀有金属矿脉：钛、钴、金（钛两处），以及三处晶簇：紫水晶、蓝晶石（紫水晶两处）。靠近目标按住 `E` 开采，触屏沿用采集按钮。金属需 1.6 秒和 4 体力，水晶需 1.2 秒和 3 体力。矿脉分别在 240 秒、180 秒后恢复。洞内两只巨蛛和一条大型洞穴蛇会近距离伤人，可用 `K` 或触屏攻击；击败后 180 秒重生。五种新资源数量显示在生存状态，随现有本地存档写入；旧存档缺少该记录时按零处理。矿点的恢复倒计时也随存档保存。

Blender 制作入口：`tools/build_hill_mine.py`。使用 Blender 5.1 后台运行，`--` 后传入绝对临时目录；脚本只覆盖该目录内的五组 `.blend` 与 `.glb`。验看后安装到 `sources/models/hill-mine-*-source.blend` 与 `assets/models/hill-mine-*.glb`。场景定义在 `scenes/Game/objects/HillMine*.settings`，实例在 `scenes/Game/external-layout/GameSurvival.settings`，逻辑在 `scenes/Game/external-events/HillMine.events`。
