"""Generate catalog-backed native events for this demo; reruns replace only our marked section."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];F=P/'scenes/Game/functions/sceneUpdate.events'
s=F.read_text(encoding='utf-8');marker='@comment "Wildlife and survival audio"'
s=s.split(marker)[0].rstrip()+'\n\n'
def q(v):return json.dumps(v,ensure_ascii=False)
def ex(v):return 'expr('+v+')'
def nv(k,op,v):return f'if NumberVariable variable={q(k)} comparison_sign={q(op)} value={v}'
def ov(o,k,op,v):return f'if NumberObjectVariable object={q(o)} variable={q(k)} comparison_sign={q(op)} value={v}'
def setv(k,v,op='='):return f'do SetNumberVariable variable={q(k)} modification_sign={q(op)} value={v}'
def seto(o,k,v,op='='):return f'do SetNumberObjectVariable object={q(o)} variable={q(k)} modification_sign={q(op)} value={v}'
def pos(o,axis,v):return f'do Set{axis} object={q(o)} modification_sign="=" value={v}'
def txt(o,t):
 if t.startswith('"') and '\n' in json.loads(t):t=ex(' + NewLine() + '.join(q(part) for part in json.loads(t).split('\n')))
 return f'do TextContainerCapability::TextContainerBehavior::SetValue object={q(o)} behavior="Text" modification_sign="=" text={t}'
def notice(t):return f'do SetStringVariable variable="NoticeMessage" modification_sign="=" value={q(t)}'
def sound(f,vol=65):return f'do PlaySound audio_file_or_audio_resource_name={q(f+".wav")} repeat_the_sound=false volume={vol} pitch_speed=1'
def anim(o,name):return f'do AnimatableCapability::AnimatableBehavior::SetName object={q(o)} behavior="Animation" modification_sign="=" animation_name={q(name)}'
def dist(a,b):return f'DistanceBetweenPositions({a}.X(), {a}.Y(), {b}.X(), {b}.Y())'
def angle(o,x,y):return f'do SetAngle object={q(o)} modification_sign="=" angle_in_degrees=expr(AngleBetweenPositions({o}.X(), {o}.Y(), {x}, {y}) - 90)'
lines=[marker+' background=[160,110,80] text=[255,255,255]','']
def event(conds,actions):lines.extend(conds+actions+[''])
active=[nv('Mode','=',0),nv('RenderMode','=',1),nv('Dead','=',0)]
key=lambda k:f'if KeyFromTextReleased key_to_check={q(k)}'
# Audio starts on a deliberate interaction so WebAudio can unlock in web exports.
event([nv('MusicStarted','=',0),'if MouseButtonFromTextPressed button_to_check="Left"','or MouseButtonFromTextPressed button_to_check="Right"','or KeyFromTextPressed key_to_check="w"','or KeyFromTextPressed key_to_check="e"','or KeyFromTextPressed key_to_check="Tab"','or KeyFromTextPressed key_to_check="m"'],[
 'do PlayMusicOnChannel audio_file_or_audio_resource_name="island-dawn.wav" channel_identifier=20 repeat_the_sound=true volume=55 pitch_speed=1',
 'do PlayMusicOnChannel audio_file_or_audio_resource_name="predator-pulse.wav" channel_identifier=21 repeat_the_sound=true volume=0 pitch_speed=1',setv('MusicStarted',1)])
event([key('m')],[setv('Muted',ex('1 - Muted'))])
event([nv('Mode','=',0),'if IsCursorOnObject object="AudioButton" accurate_test_yes_by_default=false','if MouseButtonFromTextReleased button_to_check="Left"'],[setv('Muted',ex('1 - Muted'))])
event([nv('Muted','=',0)],['do SetGlobalVolume modification_sign="=" volume_0_100=85',txt('AudioLabel',q('M 声音：开启'))])
event([nv('Muted','=',1)],['do SetGlobalVolume modification_sign="=" volume_0_100=0',txt('AudioLabel',q('M 声音：静音'))])
event([nv('MusicStarted','=',1)],[setv('ThreatMix',ex('ThreatMix + (Threat * 48 - ThreatMix) * min(1, TimeDelta() * 1.8)')),'do SetMusicChannelVolume channel_identifier=20 modification_sign="=" volume_0_100=expr(55 - ThreatMix * 0.45)','do SetMusicChannelVolume channel_identifier=21 modification_sign="=" volume_0_100=expr(ThreatMix)'])
event([nv('Mode','!=',ex('AudioMode'))],[sound('ui-click',32),setv('AudioMode',ex('Mode'))])
event([nv('Riding','!=',ex('AudioRiding'))],[sound('mount',60),setv('AudioRiding',ex('Riding'))])
event(active,[setv('Threat',0),setv('NearestWild',9999),setv('SafeCamp',0),setv('CombatHit',0),setv('Invulnerable',ex('max(0, Invulnerable - TimeDelta())')),setv('HitFlash',ex('max(0, HitFlash - TimeDelta())')),setv('CombatCD',ex('max(0, CombatCD - TimeDelta())')),setv('CombatSwing',ex('max(0, CombatSwing - TimeDelta())')),setv('StepClock',ex('max(0, StepClock - TimeDelta())')),setv('SoundClock',ex('SoundClock + TimeDelta()'))])
event(active+[nv('PreviousX','!=',ex('Player3D.X()')), 'or NumberVariable variable="PreviousY" comparison_sign="!=" value=expr(Player3D.Y())',nv('StepClock','<=',0),nv('Riding','=',0)],[sound('footstep',28),setv('StepClock',.40)])
event(active+[nv('DinoMoving','>',.01),nv('StepClock','<=',0),nv('Riding','=',1)],[sound('dino-step',50),setv('StepClock',.42)])
event(active,[setv('SafeCamp',ex('DistanceBetweenPositions(Player3D.X(), Player3D.Y(), -650, 350)'))])
# SafeCamp=1 inside the camp refuge, otherwise 0.
event(active+[nv('SafeCamp','<',330)],[setv('SafeCamp',1)])
event(active+[nv('SafeCamp','>=',330)],[setv('SafeCamp',0)])
event(active+[nv('SafeCamp','=',1),nv('Health','<',100)],[setv('Health',ex('min(100, Health + TimeDelta() * 4)'))])
event(active+[key('Space'),nv('Riding','=',0),nv('CombatCD','<=',0),nv('Stamina','>=',3)],[setv('CombatCD',.65),setv('CombatSwing',.30),setv('CombatHit',1),setv('Stamina',ex('max(0, Stamina - 3)')),setv('Dirty',1),sound('swing',50)])
# Each species is a unique instance. Per-species native state avoids group picking ambiguity.
config=[('Triceratops','三角龙',0,520,0,85),('Stegosaur','剑龙',0,500,0,75),('Raptor','迅猛龙',1,720,12,190),('Tyrannosaur','霸王龙',1,650,24,325)]
for o,label,carn,detect,damage,reach in config:
 V=lambda k:f'{o}.Variable({k})'
 alive=active+[ov(o,'HP','>',0)]
 event(alive,[seto(o,'PX',ex(o+'.X()')),seto(o,'PY',ex(o+'.Y()')),seto(o,'PA',ex(o+'.Angle()')),seto(o,'Clock',ex(V('Clock')+' + TimeDelta()')),seto(o,'AIClock',ex(V('AIClock')+' + TimeDelta()')),seto(o,'Cooldown',ex('max(0, '+V('Cooldown')+' - TimeDelta())')),seto(o,'Distance',ex(dist(o,'Player3D'))),seto(o,'Travel',0)])
 event(alive+[ov(o,'State','!=',3)], [seto(o,'State',0)])
 # Slow grazing/patrol cycles return toward a bounded home region.
 event(alive+[ov(o,'State','!=',3),ov(o,'AIClock','>',4)], [seto(o,'State',1),seto(o,'TargetX',ex(V('HomeX')+' + cos('+V('Clock')+' * 0.23) * 145')),seto(o,'TargetY',ex(V('HomeY')+' + sin('+V('Clock')+' * 0.23) * 110'))])
 event(alive+[ov(o,'AIClock','>',9)],[seto(o,'AIClock',0)])
 if carn:
  event(alive+[ov(o,'Distance','<',detect),nv('SafeCamp','=',0),ov(o,'State','!=',3),nv('Invulnerable','<=',0)],[seto(o,'State',2),seto(o,'TargetX',ex('Player3D.X()')),seto(o,'TargetY',ex('Player3D.Y()')),setv('Threat',1)])
  event(alive+[ov(o,'State','>=',2)],[setv('Threat',1)])
  event(alive+[ov(o,'State','=',2),ov(o,'Distance','<=',ex(str(reach+65)+' + Riding * 320')),ov(o,'Cooldown','<=',0)],[seto(o,'State',3),seto(o,'Windup',.85),seto(o,'DamageDone',0),seto(o,'Cooldown',2.2),sound('raptor-call' if o=='Raptor' else 'rex-roar',45)])
  event(alive+[ov(o,'State','=',3)],[seto(o,'Windup',ex(V('Windup')+' - TimeDelta()')),angle(o,'Player3D.X()','Player3D.Y()')])
  event(alive+[ov(o,'State','=',3),ov(o,'Windup','<=',.30),ov(o,'DamageDone','=',0)],[seto(o,'DamageDone',1)])
  # DamageDone=1 is a one-frame contact window; distance is checked again so dodging works.
  event(alive+[ov(o,'State','=',3),ov(o,'DamageDone','=',1),ov(o,'Distance','<=',ex(str(reach+85)+' + Riding * 320')),nv('Invulnerable','<=',0),nv('SafeCamp','=',0)],[setv('Health',ex(f'max(0, Health - {damage} + Riding * {damage*.5})')),setv('Invulnerable',1),setv('HitFlash',.35),setv('Dirty',1),notice(label+'撕咬！拉开距离，空格反击或骑乘撤离。'),sound('hurt',75),sound('bite',65)])
  event(alive+[ov(o,'DamageDone','=',1)],[seto(o,'DamageDone',2)])
  event(alive+[ov(o,'State','=',3),ov(o,'Windup','<=',0)],[seto(o,'State',0)])
 # Patrol and chase; stop just outside head contact when chasing.
 for state in [1,2] if carn else [1]:
  cond=alive+[ov(o,'State','=',state)]
  if state==2:cond+=[ov(o,'Distance','>',ex(str(reach+20)+' + Riding * 320'))]
  speed=ex(V('Speed')+(' * 0.30' if state==1 else ''))
  event(cond,[angle(o,V('TargetX'),V('TargetY')),pos(o,'X',ex(o+'.X() - sin(ToRad('+o+'.Angle())) * '+speed[5:-1]+' * TimeDelta()')),pos(o,'Y',ex(o+'.Y() + cos(ToRad('+o+'.Angle())) * '+speed[5:-1]+' * TimeDelta()'))])
 # Ground-plane bounds and cabin rollback. Avoid setting position by a large discontinuity.
 rollback=[pos(o,'X',ex(V('PX'))),pos(o,'Y',ex(V('PY')))]
 for axis,op,value in [('X','<',-1400),('X','>',1400),('Y','<',-1500),('Y','>',1000)]:event(alive+[f'if Pos{axis} object="{o}" comparison_sign="{op}" value={value}'],rollback)
 event(alive+[f'if PosX object="{o}" comparison_sign=">" value=expr(-1250 - {V("Radius")})',f'if PosX object="{o}" comparison_sign="<" value=expr(-550 + {V("Radius")})',f'if PosY object="{o}" comparison_sign=">" value=expr(-1010 - {V("Radius")})',f'if PosY object="{o}" comparison_sign="<" value=expr(-380 + {V("Radius")})'],rollback)
 # Capsule covers torso and tail, rotates with heading. Expanded by player radius.
 event(alive+[nv('Riding','=',0)],[seto(o,'LocalX',ex(f'(Player3D.X() - {o}.X()) * cos(ToRad({o}.Angle())) + (Player3D.Y() - {o}.Y()) * sin(ToRad({o}.Angle()))')),seto(o,'LocalY',ex(f'-(Player3D.X() - {o}.X()) * sin(ToRad({o}.Angle())) + (Player3D.Y() - {o}.Y()) * cos(ToRad({o}.Angle()))')),seto(o,'NearY',ex(f'clamp({V("LocalY")}, -{V("HalfLength")} + {V("Radius")}, {reach} - {V("Radius")})')),seto(o,'Separation',ex(f'max(0.001, sqrt({V("LocalX")} * {V("LocalX")} + pow({V("LocalY")} - {V("NearY")}, 2)))'))])
 event(alive+[nv('Riding','=',0),ov(o,'Separation','<=',.001)],[seto(o,'LocalX',ex(V('Radius')+' + 45')),seto(o,'Separation',ex(V('Radius')+' + 45'))])
 event(alive+[nv('Riding','=',0),ov(o,'Separation','<',ex(V('Radius')+' + 45'))],[seto(o,'LocalX',ex(f'{V("LocalX")} * ({V("Radius")} + 45) / {V("Separation")}')),seto(o,'LocalY',ex(f'{V("NearY")} + ({V("LocalY")} - {V("NearY")}) * ({V("Radius")} + 45) / {V("Separation")}')),pos('Player3D','X',ex(f'{o}.X() + {V("LocalX")} * cos(ToRad({o}.Angle())) - {V("LocalY")} * sin(ToRad({o}.Angle()))')),pos('Player3D','Y',ex(f'{o}.Y() + {V("LocalX")} * sin(ToRad({o}.Angle())) + {V("LocalY")} * cos(ToRad({o}.Angle()))'))])
 # Reserve conservative clearance around the mount, including long tails.
 event(alive+[f'if Distance object="{o}" object_2="Dinosaur3D" distance=expr({V("HalfLength")} + 390)'],rollback)
 event(alive+[nv('Riding','=',1),f'if Distance object="{o}" object_2="Dinosaur3D" distance=expr({V("HalfLength")} + 380)'],[pos('Dinosaur3D','X',ex('DinoPreviousX')),pos('Dinosaur3D','Y',ex('DinoPreviousY'))])
 if carn:
  # Space attacks nearest predator in range; thrust is aimed at that creature.
  attack=alive+[nv('CombatHit','=',1),ov(o,'Distance','<',ex(V('HalfLength')+' + 200')),ov(o,'State','!=',4)]
  event(attack,[seto(o,'HP',ex(V('HP')+' - (12 + min(1, Spear) * 23)')),setv('CombatHit',0),setv('CombatLesson',1),angle('Player3D',o+'.X()',o+'.Y()'),sound('bite',60),notice('命中'+label+'！继续保持距离。'),setv('Dirty',1)])
  event(active+[ov(o,'HP','<=',0),ov(o,'State','!=',4)],[seto(o,'State',4),seto(o,'Respawn',45),f'do Hide object="{o}"',setv('Kills',1,'+'),setv('Meat',3,'+'),setv('Hide',2,'+'),notice('击退'+label+'：生肉 +3、兽皮 +2。'),sound('pickup',70),setv('Dirty',1)])
  event(active+[ov(o,'State','=',4)],[seto(o,'Respawn',ex(V('Respawn')+' - TimeDelta()'))])
  event(active+[ov(o,'State','=',4),ov(o,'Respawn','<=',0),f'@instruction inverted=true',f'if Distance object="{o}" object_2="Player3D" distance=900'],[seto(o,'HP',ex(V('MaxHP'))),seto(o,'State',0),seto(o,'Cooldown',3),pos(o,'X',ex(V('HomeX'))),pos(o,'Y',ex(V('HomeY'))),f'do Show object="{o}"'])
 event(alive,[seto(o,'Travel',ex(f'DistanceBetweenPositions({V("PX")}, {V("PY")}, {o}.X(), {o}.Y())'))])
 event(alive+[ov(o,'Travel','>',.01),ov(o,'State','!=',3)],[anim(o,'Walk'),seto(o,'AnimationState',1)])
 event(alive+[ov(o,'Travel','<=',.01),ov(o,'State','!=',3)],[anim(o,'Idle'),seto(o,'AnimationState',0)])
 if carn:event(alive+[ov(o,'State','=',3)],[anim(o,'Attack'),seto(o,'AnimationState',2)])
 event(alive,[f'do AnimatableCapability::AnimatableBehavior::PlayAnimation object="{o}" behavior="Animation"'])
 event([nv('Mode','!=',0),'or NumberVariable variable="RenderMode" comparison_sign="!=" value=1'],[f'do AnimatableCapability::AnimatableBehavior::PauseAnimation object="{o}" behavior="Animation"'])
 event(alive+[ov(o,'Distance','<',ex('NearestWild'))],[setv('NearestWild',ex(V('Distance'))),txt('WildHint',ex(q(label+(' · 食肉 / 危险' if carn else ' · 食草 / 温顺'))+' + "  " + ToString(round('+V('Distance')+' / 100)) + "m" + NewLine() + '+(q('生命 ')+f' + ToString(max(0, {V("HP")})) + '+q(' · 空格反击 / X 骑乘撤离') if carn else q('缓慢觅食中 · 保持距离观察'))))])
# Pairwise wildlife clearance uses bounding circles; rollback the later mover.
for i,(a,*_) in enumerate(config):
 for b,*_ in config[i+1:]:
  event(active+[ov(a,'HP','>',0),ov(b,'HP','>',0),f'if Distance object="{a}" object_2="{b}" distance=expr({a}.Variable(HalfLength) + {b}.Variable(HalfLength))'],[pos(a,'X',ex(a+'.Variable(PX)')),pos(a,'Y',ex(a+'.Variable(PY)')),pos(b,'X',ex(b+'.Variable(PX)')),pos(b,'Y',ex(b+'.Variable(PY)'))])
# Keep camera/rider in sync after collision rollback.
event(active+[nv('Riding','=',1)],[pos('Player3D','X',ex('Dinosaur3D.X()')),pos('Player3D','Y',ex('Dinosaur3D.Y()')),pos('MountedRider','X',ex('Dinosaur3D.X() + sin(ToRad(Dinosaur3D.Angle())) * 15')),pos('MountedRider','Y',ex('Dinosaur3D.Y() - cos(ToRad(Dinosaur3D.Angle())) * 15'))])
event([nv('Mode','>=',0)],['do Hide object="CombatSpear"','do Hide object="DeathPanel"','do Hide object="DeathText"','do Hide object="DamageFlash"',txt('Value0',ex('ToString(round(Health)) + " / 100"')),'do ResizableCapability::ResizableBehavior::SetWidth object="Meter0" behavior="Resizable" modification_sign="=" width=expr(max(0, Health) * 1.98)'])
event(active+[nv('Spear','>',0),nv('Riding','=',0),nv('CombatSwing','>',0)],['do Show object="CombatSpear"','do Hide object="HeldAxe"',pos('CombatSpear','X',ex('Player3D.X() - cos(ToRad(Player3D.Angle())) * 40 - sin(ToRad(Player3D.Angle())) * CombatSwing * 170')),pos('CombatSpear','Y',ex('Player3D.Y() - sin(ToRad(Player3D.Angle())) * 40 + cos(ToRad(Player3D.Angle())) * CombatSwing * 170')),'do SetAngle object="CombatSpear" modification_sign="=" angle_in_degrees=expr(Player3D.Angle())'])
event(active+[nv('Spear','<=',0),nv('CombatSwing','>',0)],[setv('SelectedHotbar',1),setv('AxeSwing',ex('CombatSwing'))])
event(active+[nv('HitFlash','>',0)],['do Show object="DamageFlash"','do OpacityCapability::OpacityBehavior::SetValue object="DamageFlash" behavior="Opacity" modification_sign="=" opacity_0_255=expr(HitFlash / 0.35 * 190)'])
event(active+[nv('SoundClock','>',18),nv('Threat','=',0)],[sound('herbivore-call',22),setv('SoundClock',0)])
event(active+[nv('Health','<=',0)],[setv('Dead',1),setv('Mode',7),setv('DeathCount',1,'+'),setv('Riding',0),setv('Threat',0),sound('death',75)])
event([nv('Dead','=',1)],[setv('Mode',7),'do ShowLayer layer="HUD"','do Show object="DeathPanel"','do Show object="DeathText"','do Hide object="CombatSpear"','do Hide object="HeldAxe"',txt('DeathText',ex('"你倒下了" + NewLine() + NewLine() + "按 Enter 在营地重生" + NewLine() + "保留工具，损失 3 浆果和 1 生肉" + NewLine() + "下次带上长矛，或骑乘逃离追击。"'))])
event([nv('Dead','=',1),key('Return')],[setv('Dead',0),setv('Mode',0),setv('Health',100),setv('Invulnerable',5),setv('HitFlash',0),setv('StationIndex',1),setv('Berries',ex('max(0, Berries - 3)')),setv('Meat',ex('max(0, Meat - 1)')),setv('Stamina',80),setv('Water',80),pos('Player3D','X',-650),pos('Player3D','Y',350),setv('PreviousX',-650),setv('PreviousY',350),notice('已在营地重生，获得 5 秒保护。'),sound('respawn',70),setv('Dirty',1)])
# UI tutorial always supplies an actionable danger response.
event(active+[nv('SafeCamp','=',1)],[txt('WildHint',q('营地庇护 · 生命缓慢恢复\n出发前制作长矛；空格反击，X 骑乘撤离'))])
event(active+[nv('NearestWild','>',1100),nv('SafeCamp','=',0)],[txt('WildHint',q('荒野探索 · 共 5 种恐龙\n2 制作长矛 · 空格反击 · M 声音'))])
# Existing action receipts get their own sound, never inferred from repeated HUD refreshes.
if 'audio_file_or_audio_resource_name="feed.wav"' not in s:
 s=s.replace('do SetNumberVariable variable="Trust" modification_sign="+" value=7','do SetNumberVariable variable="Trust" modification_sign="+" value=7\n'+sound('feed'))
 s=s.replace('do SetNumberVariable variable="Built" modification_sign="=" value=1','do SetNumberVariable variable="Built" modification_sign="=" value=1\n'+sound('build'))
 s=s.replace('do SetNumberVariable variable="Water" modification_sign="=" value=100','do SetNumberVariable variable="Water" modification_sign="=" value=100\n'+sound('drink',50))
 for item in ['Spear','Axe']:s=s.replace(f'do SetNumberVariable variable="{item}" modification_sign="+" value=1',f'do SetNumberVariable variable="{item}" modification_sign="+" value=1\n'+sound('craft'))
 s=s.replace('audio_file_or_audio_resource_name="harvest.wav" repeat_the_sound=false volume=45 pitch_speed=1.3','audio_file_or_audio_resource_name="quest-complete.wav" repeat_the_sound=false volume=60 pitch_speed=1')
 s=s.replace('Spear: choose Craft to make one. Combat is not available in this demo.','长矛：制作后按空格反击食肉恐龙。')
 s=s.replace('Bandage: health is already full. No bandage consumed.','受伤后返回营地，生命会缓慢恢复。')
 s=s.replace('Welcome. Feed your first companion with E.','探索海岛，收集物资。北部有食肉恐龙；2 制作长矛，空格反击。')
F.write_text(s+'\n'.join(lines),encoding='utf-8')
print('Authored wildlife, combat, respawn and dynamic audio with native events')
