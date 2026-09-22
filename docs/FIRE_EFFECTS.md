# 营火动态效果

营地篝火与玩家建造的篝火共用 `SurvivalFires`。有燃料时，火焰模型持续改变高度、宽度和小角度朝向，火星随机升起、漂移、变暗、缩小后消失。火星是 World3D 中的轻量 3D 对象，参与场景遮挡，不是贴在屏幕上的效果。

- 每堆近处营火约每 0.075 秒发射一次，火星寿命 0.8–1.65 秒。
- 全场最多 96 个火星，只给距玩家 1800 单位以内的燃烧营火发射。
- 燃料耗尽停止发射，余下火星自然消失；再次加柴自动恢复。
- 暂停、死亡和参考图模式冻结动画；读取存档清理旧粒子。粒子不写入存档。
- 使用现有火焰 GLB、原生 3D 方块与 IfDo 事件，无额外贴图、插件或物理模拟。静态火焰模型保留低多边形风格。

实现：`scenes/Game/external-events/FireParticles.events`、`scenes/Game/objects/FireEmber.settings`、`FireGlow.settings`。验证：`tests/FireParticles.js`，并回归 `tests/SurvivalSupplies.js` 的加柴和烹饪流程。
