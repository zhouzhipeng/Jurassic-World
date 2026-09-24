# 西山矿洞

主岛西侧小山的东坡已挖出开放式入口，约从 `(-1450, 600)` 向西下切至山体内部。山体网格的地表在入口处真实开口，保留洞内上方的山体屋顶；衬砌、木支架、照明、矿脉、水晶和洞穴生物使用独立 3D 模型。玩家进入后切换到洞底缓坡，离开时回到主岛原有地形高度。通道两侧限制穿墙，洞内镜头缩近。

洞内有四处稀有金属矿脉：钛、钴、金（钛两处），以及三处晶簇：紫水晶、蓝晶石（紫水晶两处）。靠近目标按住 `E` 开采，触屏沿用采集按钮。金属需 1.6 秒和 4 体力，水晶需 1.2 秒和 3 体力。矿脉分别在 240 秒、180 秒后恢复。洞内两只巨蛛和一条大型洞穴蛇会近距离伤人，可用 `K` 或触屏攻击；击败后 180 秒重生。五种新资源数量显示在生存状态，随现有本地存档写入；旧存档缺少该记录时按零处理。矿点的恢复倒计时也随存档保存。

Blender 制作入口：`tools/carve_hill_mine.py` 读取保留的 `sources/environment/island-coast-source.blend`，生成新可编辑地形 `sources/environment/island-mine-source.blend` 与 `assets/models/island.glb`。`tools/build_hill_mine.py` 生成五组洞内 `.blend` 与 `.glb`。两者使用 Blender 5.1 后台运行，`--` 后传入绝对临时目录，只覆盖该目录；验看后再安装。场景定义在 `scenes/Game/objects/HillMine*.settings`，实例在 `scenes/Game/external-layout/GameSurvival.settings`，洞底切换在 `scenes/Game/external-events/HillMineTerrain.events`，采矿和生物逻辑在 `scenes/Game/external-events/HillMine.events`。
