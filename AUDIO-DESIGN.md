# 岛屿初曦 — 生存 Demo 声音设计

探索曲为原创合成配乐：80 BPM、D 小调五声音阶、16 小节、48 秒循环。低音木质拨弦提供脉动，中音木琴式音色和带气息的笛声轮流呈现短旋律，手鼓与轻沙响保持空间感。循环采用环形延迟保存尾音，无外部采样或现成歌曲。

`island-dawn.wav` 与 `predator-pulse.wav` 同时从 0 秒开始循环。后者默认静音，食肉恐龙进入追击或攻击时渐入低鼓和低音节奏，探索层同时降低音量；脱离危险后恢复。音乐使用独立频道 20、21；交互音效不占用这两个频道。首次互动启动，M 或 HUD 声音按钮切换全局声音。

| 场景 | 文件 / 设计 |
|---|---|
| 探索 | island-dawn.wav，48 秒、立体声 |
| 追击 | predator-pulse.wav，48 秒、立体声，渐入危险节奏 |
| 步行 / 骑乘 | footstep.wav / dino-step.wav，脚步与低沉落足，按移动节奏触发 |
| 采集 / 砍树 | 沿用 harvest.wav、axe-hit.wav，动作成功时触发 |
| 喂食 / 上下坐骑 | feed.wav / mount.wav，短促柔和回应 |
| 制作 / 营地加固 | craft.wav / build.wav，完成提示与木质敲击 |
| 饮水 | drink.wav，合成水泡声 |
| 菜单开关 | ui-click.wav，低音量木质提示 |
| 任务达成 / 战利品 | quest-complete.wav / pickup.wav，上行短音型 |
| 反击 / 撕咬 / 受伤 | swing.wav / bite.wav / hurt.wav，空气掠过、咬合、低频冲击 |
| 迅猛龙 / 霸王龙 | raptor-call.wav / rex-roar.wav，攻击前的警告叫声 |
| 平静生态 | herbivore-call.wav，间歇低音量鸣叫 |
| 倒下 / 重生 | death.wav / respawn.wav，下行低音与恢复短句 |

全部新音频为 32 kHz、16-bit PCM WAV；音效单声道，BGM 双声道。生成脚本记录时长和峰值，输出无硬削波。可用 `tools/compose_audio.py` 重新生成，清单为 `assets/audio/audio-manifest.json`。

当前是程序合成配乐与拟音版本。后续可在保持文件名和触发事件的情况下替换为录制拟音、演奏或更细致的恐龙声素材。
