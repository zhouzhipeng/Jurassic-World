"""Project-specific native construction events, no JavaScript runtime dependency."""
from pathlib import Path
if (Path(__file__).resolve().parents[1] / "extensions/JurassicActors").exists():
    raise SystemExit("This one-shot generator targets the pre-prefab layout. Edit scene external events and JurassicActors prefab sources directly.")
import json,re
P=Path(__file__).resolve().parents[1];F=P/'scenes/Game/functions/sceneUpdate.events'
s=F.read_text(encoding='utf-8');marker='@comment "Construction placement and persistence"';endmarker='@comment "Player skeletal animation controller"'
if marker in s:s=s[:s.index(marker)]+s[s.index(endmarker):]
q=lambda x:json.dumps(x,ensure_ascii=False)
ex=lambda x:'expr('+str(x)+')'
def nv(k,op='=',v=0):return f'if NumberVariable variable={q(k)} comparison_sign={q(op)} value={v}'
def ov(o,k,op,v):return f'if NumberObjectVariable object={q(o)} variable={q(k)} comparison_sign={q(op)} value={v}'
def cmp(a,op,b):return f'if BuiltinCommonInstructions::CompareNumbers first_expression={ex(a)} comparison_sign={q(op)} second_expression={ex(b)}'
def sv(k,v,op='='):return f'do SetNumberVariable variable={q(k)} modification_sign={q(op)} value={v}'
def so(o,k,v,op='='):return f'do SetNumberObjectVariable object={q(o)} variable={q(k)} modification_sign={q(op)} value={v}'
def st(k,v):return f'do SetStringVariable variable={q(k)} modification_sign="=" value={q(v)}'
def txt(o,v):return f'do TextContainerCapability::TextContainerBehavior::SetValue object={q(o)} behavior="Text" modification_sign="=" text={v}'
def key(k):return f'if KeyFromTextReleased key_to_check={q(k)}'
def xy(o,x,y):return [f'do SetX object={q(o)} modification_sign="=" value={ex(x)}',f'do SetY object={q(o)} modification_sign="=" value={ex(y)}']
def event(cs,acts,depth=0):return '\n'.join(('>'*depth+' ' if depth else '')+l for l in cs+acts)+'\n\n'
def sound(n='build'):return f'do PlaySound audio_file_or_audio_resource_name="{n}.wav" repeat_the_sound=false volume=60 pitch_speed=1'
play=[nv('Mode'),nv('RenderMode','=',1),nv('Riding')];build=play+[nv('BuildMode','=',1)]
names=['BuiltShelter','BuiltPalisade','BuiltCampfire'];costs=[(10,5,8),(4,0,2),(3,3,0)];extents=[(240,205),(200,25),(80,80)]
# Block overlapping survival shortcuts while building; movement and camera remain active.
if '@comment "Construction input"' not in s:
 blocks=s.split('\n\n')
 for i,b in enumerate(blocks):
  if (('if NumberVariable variable="Mode" comparison_sign="=" value=0' in b or 'if NumberVariable variable="InputMode" comparison_sign="=" value=0' in b) and ('KeyFromText' in b or 'MouseButton' in b)):
   if re.search(r'key_to_check="(e|r|g|f|q|x|Space|Num[1-8])"',b) or 'MouseButtonFromTextReleased button_to_check="Left"' in b or 'MouseButtonFromTextPressed button_to_check="Left"' in b:
    at=b.find('if ');b=b[:at]+nv('BuildMode')+'\n'+b[at:];blocks[i]=b
 s='\n\n'.join(blocks)
 head='@comment "Construction input" background=[120,145,90] text=[255,255,255]\n\n'
 head+=event(play+[key('b')],[sv('BuildMode',ex('1 - BuildMode'))])
 head+=event(play+['if IsCursorOnObject object="BuildToggle" accurate_test_yes_by_default=false','if MouseButtonFromTextReleased button_to_check="Left"'],[sv('BuildMode',ex('1 - BuildMode'))])
 for cs in [[nv('Mode','!=',0)],[nv('Riding','=',1)],[nv('RenderMode','=',0)]]:head+=event(cs,[sv('BuildMode',0)])
 s=head+s
 # Extend the existing save transaction. Buildings and paid inventory share one save action.
 s=s.replace('do EcrireFichierExp storage_name="JurassicWorldDemo" group="Trust"', 'do EcrireFichierTxt storage_name="JurassicWorldDemo" group="BuildingsV1" text=expr(ToJSON(BuildingRecords))\ndo EcrireFichierExp storage_name="JurassicWorldDemo" group="Trust"',1)
 # Read requested before the existing load event clears Action.
 hook=event([nv('Action','=',10),'if GroupExists storage_name="JurassicWorldDemo" group="Version"'],[st('BuildJSON','[]'),sv('BuildRestore',1),sv('BuildMode',0)])
 hook+=event([nv('Action','=',10),'if GroupExists storage_name="JurassicWorldDemo" group="BuildingsV1"'],['do ReadStringFromStorage storage_name="JurassicWorldDemo" group="BuildingsV1" variable="BuildJSON"'])
 anchor='if NumberVariable variable="Action" comparison_sign="=" value=10\nif GroupExists storage_name="JurassicWorldDemo" group="Version"'
 assert anchor in s;s=s.replace(anchor,hook+anchor,1)
 s=s.replace('WASD 移动 · Shift 奔跑 · E 采集','WASD 移动 · Shift 奔跑 · B 建造 · E 采集')
 # Old camp reinforcement now opens actual shelter placement and charges only on placement.
 start=s.index('if NumberVariable variable="Action" comparison_sign="=" value=1\nif NumberVariable variable="StationIndex" comparison_sign="=" value=1')
 end=s.index('if NumberVariable variable="Action" comparison_sign="=" value=2',start)
 s=s[:start]+event([nv('Action','=',1),nv('StationIndex','=',1)],[sv('BuildMode',1),sv('BuildKind',1),sv('Action',0),st('NoticeMessage','选择空地搭建庇护所，完成营地任务。'),sv('Dirty',1)])+s[end:]
 s=s.replace('营地加固  ','建造庇护所  ').replace('Build: 10 wood / 5 stone / 8 fiber','B 建造庇护所：10 木 / 5 石 / 8 纤维')
out=marker+' background=[120,145,90] text=[255,255,255]\n\n'
def create(n,x,y,angle,slot):
 return [f'do Create object_to_create={q(n)} x_position={ex(x)} y_position={ex(y)} layer="World3D"',f'do SetAngle object={q(n)} modification_sign="=" angle_in_degrees={ex(angle)}',so(n,'Slot',ex(slot)),so(n,'WorldHX',ex(f'abs(cos(ToRad({angle}))) * {n}.Variable(HX) + abs(sin(ToRad({angle}))) * {n}.Variable(HY)')),so(n,'WorldHY',ex(f'abs(sin(ToRad({angle}))) * {n}.Variable(HX) + abs(cos(ToRad({angle}))) * {n}.Variable(HY)'))]
out+=event([nv('BuildRestore','=',1)],['do Delete object="Buildings"','do JSONToVariableStructure2 json_string=expr(BuildJSON) variable_where_to_store_the_json_object="BuildingRecords"',sv('BuildCount',0)])
out+='> local i = 0\n> repeat 40 index=i\n'
for kind,n in enumerate(names,1):out+=event([nv('BuildingRecords[i].Kind','=',kind)],create(n,'BuildingRecords[i].X','BuildingRecords[i].Y','BuildingRecords[i].Angle','i')+[sv('BuildCount',1,'+')],2)
out+=event([nv('BuildRestore','=',1)],[sv('BuildRestore',0)])
# Default UI and diagnostics, including out-of-build near-fire feedback.
ui=['BuildPanel','BuildTitle','BuildStatus']+['BuildChoice'+suf+str(i) for i in range(1,4) for suf in ['', 'Label']]
out+=event([nv('Mode','>=',0)],['do Hide object="BuildGhosts"']+[f'do Hide object={q(o)}' for o in ui]+[sv('BuildWarm',0),sv('BuildRest',0)])
out+=event(play,[f'do Show object={q(o)}' for o in ['BuildToggle','BuildToggleLabel']])
out+=event([nv('Mode','!=',0)],['do Hide object="BuildToggle"','do Hide object="BuildToggleLabel"'])
for kind,n in enumerate(names,1):
 out+=event(build+[key('Num'+str(kind))],[sv('BuildKind',kind)])
 out+=event(build+[f'if IsCursorOnObject object="BuildChoice{kind}" accurate_test_yes_by_default=false','if MouseButtonFromTextReleased button_to_check="Left"'],[sv('BuildKind',kind)])
out+=event(build+[key('r')],[sv('BuildAngle',ex('mod(BuildAngle + 90, 360)'))])
out+=event(build,[sv('BuildX',ex('round((Player3D.X() - sin(ToRad(CameraYaw)) * 450) / 100) * 100')),sv('BuildY',ex('round((Player3D.Y() - cos(ToRad(CameraYaw)) * 450) / 100) * 100')),sv('BuildValid',1),sv('BuildSlot',-1),st('BuildReason','可放置 · Enter 确认建造')])
out+='if NumberVariable variable="BuildMode" comparison_sign="=" value=1\n> local i = 0\n> repeat 40 index=i\n'+event([nv('BuildSlot','<',0),nv('BuildingRecords[i].Kind','=',0)],[sv('BuildSlot',ex('i'))],2)
for kind,((w,stone,fiber),(hx,hy)) in enumerate(zip(costs,extents),1):
 out+=event(build+[nv('BuildKind','=',kind)],[sv('BuildWood',w),sv('BuildStone',stone),sv('BuildFiber',fiber),sv('BuildHX',hx),sv('BuildHY',hy)])
out+=event(build,[sv('BuildWorldHX',ex('abs(cos(ToRad(BuildAngle))) * BuildHX + abs(sin(ToRad(BuildAngle))) * BuildHY')),sv('BuildWorldHY',ex('abs(sin(ToRad(BuildAngle))) * BuildHX + abs(cos(ToRad(BuildAngle))) * BuildHY'))])
def reject(cs,message,depth=0):return event(cs,[sv('BuildValid',0),st('BuildReason',message)],depth)
for k,c in [('Wood','BuildWood'),('Stone','BuildStone'),('Fiber','BuildFiber')]:out+=reject(build+[nv(k,'<',ex(c))],'材料不足：先采集木材、石头和纤维')
out+=reject(build+[nv('BuildSlot','<',0)],'最多保留 40 个建筑，请先拆除')
for a,b in [('abs(BuildX) + BuildWorldHX','2550'),('BuildY + BuildWorldHY','2250'),('-BuildY + BuildWorldHY','2700')]:out+=reject(build+[cmp(a,'>',b)],'越过陆地范围，向岛内移动')
out+=reject(build+[cmp('BuildX + BuildWorldHX','>','-1300'),cmp('BuildX - BuildWorldHX','<','-500'),cmp('BuildY + BuildWorldHY','>','-1060'),cmp('BuildY - BuildWorldHY','<','-330')],'与现有木屋重叠')
out+=reject(build+[cmp('DistanceBetweenPositions(BuildX, BuildY, -650, 350)','<','sqrt(BuildHX*BuildHX+BuildHY*BuildHY)+180')],'请留出营地重生区')
out+=event(build,[])+'> for each Buildings\n'+reject([cmp('abs(BuildX - Buildings.X())','<','BuildWorldHX + Buildings.Variable(WorldHX) - 1'),cmp('abs(BuildY - Buildings.Y())','<','BuildWorldHY + Buildings.Variable(WorldHY) - 1')],'与已有建筑重叠',2)
out+=event(build,[])+'> for each HarvestNodes\n'+reject([ov('HarvestNodes','Cooldown','<=',0),cmp('abs(BuildX-HarvestNodes.X())','<','BuildWorldHX+80'),cmp('abs(BuildY-HarvestNodes.Y())','<','BuildWorldHY+80')],'此处有资源，请换一块空地',2)
out+=reject(build+[cmp('DistanceBetweenPositions(BuildX,BuildY,Dinosaur3D.X(),Dinosaur3D.Y())','<','sqrt(BuildHX*BuildHX+BuildHY*BuildHY)+380')],'坐骑占用此处，请先移开')
out+=event(build,[])+'> for each Wildlife\n'+reject([ov('Wildlife','HP','>',0),cmp('DistanceBetweenPositions(BuildX,BuildY,Wildlife.X(),Wildlife.Y())','<','sqrt(BuildHX*BuildHX+BuildHY*BuildHY)+Wildlife.Variable(HalfLength)+Wildlife.Variable(Radius)')],'恐龙占用此处，请保持距离',2)
for kind,n in enumerate(names,1):
 for valid,suffix in [(1,'Valid'),(0,'Invalid')]:
  ghost=n+suffix;out+=event(build+[nv('BuildKind','=',kind),nv('BuildValid','=',valid)],xy(ghost,'BuildX','BuildY')+[f'do SetAngle object={q(ghost)} modification_sign="=" angle_in_degrees=expr(BuildAngle)',f'do Show object={q(ghost)}'])
# One released Enter produces at most one paid building. Keep browsing active afterward.
for kind,n in enumerate(names,1):
 acts=create(n,'BuildX','BuildY','BuildAngle','BuildSlot')
 acts+=[sv('BuildingRecords[BuildSlot].'+k,ex(v)) for k,v in [('Kind','BuildKind'),('X','BuildX'),('Y','BuildY'),('Angle','BuildAngle')]]
 acts += [sv('Wood',ex('BuildWood'),'-'),sv('Stone',ex('BuildStone'),'-'),sv('Fiber',ex('BuildFiber'),'-'),sv('BuildCount',1,'+'),sv('BuildValid',0),st('BuildReason','建造完成 · 移动到下一处空地'),sv('Dirty',1),sound()]
 if kind==1:acts += [sv('Built',1)]
 out+=event(build+[key('Return'),nv('BuildValid','=',1),nv('BuildKind','=',kind)],acts)
out+=event(build+[key('Return'),nv('BuildValid','=',0)],[sv('Dirty',1)])
# Select the closest building to the placement cursor for deliberate demolition.
out+=event(build,[sv('BuildDeleteDistance',9999),sv('BuildDeleteSlot',-1)])
out+=event(build,[])+'> for each Buildings\n'+event([cmp('DistanceBetweenPositions(BuildX,BuildY,Buildings.X(),Buildings.Y())','<','250'),cmp('DistanceBetweenPositions(BuildX,BuildY,Buildings.X(),Buildings.Y())','<','BuildDeleteDistance')],[sv('BuildDeleteDistance',ex('DistanceBetweenPositions(BuildX,BuildY,Buildings.X(),Buildings.Y())')),sv('BuildDeleteSlot',ex('Buildings.Variable(Slot)'))],2)
for kind,(w,stone,fiber) in enumerate(costs,1):
 out+=event(build+[key('Delete'),nv('BuildDeleteSlot','>=',0),ov('Buildings','Slot','=',ex('BuildDeleteSlot')),ov('Buildings','Kind','=',kind)],[sv('BuildingRecords[BuildDeleteSlot].Kind',0),'do Delete object="Buildings"',sv('BuildCount',1,'-'),sv('Wood',w//2,'+'),sv('Stone',stone//2,'+'),sv('Fiber',fiber//2,'+'),sv('Dirty',1),st('BuildReason','已拆除，返还一半材料'),sound()])
# Physical walls. Player can enter the shelter through its open front.
for entity,px,py,padx,pady in [('Player3D','PreviousX','PreviousY','36','36'),('Dinosaur3D','DinoPreviousX','DinoPreviousY','150 + abs(sin(ToRad(Dinosaur3D.Angle()))) * 260','150 + abs(cos(ToRad(Dinosaur3D.Angle()))) * 260'),('Wildlife','Wildlife.Variable(PX)','Wildlife.Variable(PY)','Wildlife.Variable(Radius) + abs(sin(ToRad(Wildlife.Angle()))) * Wildlife.Variable(HalfLength)','Wildlife.Variable(Radius) + abs(cos(ToRad(Wildlife.Angle()))) * Wildlife.Variable(HalfLength)')]:
 cs=[nv('Mode'),nv('RenderMode','=',1)]
 if entity=='Player3D':cs+=[nv('Riding')]
 out+=event(cs,[])+'> for each Buildings\n'
 depth=2
 if entity=='Wildlife':out+='>> for each Wildlife\n';depth=3
 inside=[cmp(f'abs({entity}.X()-Buildings.X())','<',f'Buildings.Variable(WorldHX)+({padx})'),cmp(f'abs({entity}.Y()-Buildings.Y())','<',f'Buildings.Variable(WorldHY)+({pady})')]
 if entity=='Player3D':
  out+=event(inside,[sv('BuildLX',ex('(Player3D.X()-Buildings.X())*cos(ToRad(Buildings.Angle()))+(Player3D.Y()-Buildings.Y())*sin(ToRad(Buildings.Angle()))')),sv('BuildLY',ex('-(Player3D.X()-Buildings.X())*sin(ToRad(Buildings.Angle()))+(Player3D.Y()-Buildings.Y())*cos(ToRad(Buildings.Angle()))'))],depth)
  out+=event([ov('Buildings','Kind','!=',1)],xy(entity,px,py),depth+1)
  out+=event([ov('Buildings','Kind','=',1),cmp('abs(BuildLX)','>','145'),'or BuiltinCommonInstructions::CompareNumbers first_expression=expr(BuildLY) comparison_sign="<" second_expression=-130'],xy(entity,px,py),depth+1)
 else:
  acts=xy(entity,px,py)+[so(entity,'AnimationState',0),f'do AnimatableCapability::AnimatableBehavior::SetName object={q(entity)} behavior="Animation" modification_sign="=" animation_name="Idle"']
  if entity=='Dinosaur3D':
   out+=event(inside,acts,depth);out+=event([nv('Riding','=',1)],xy('Player3D','Dinosaur3D.X()','Dinosaur3D.Y()')+xy('MountedRider','Dinosaur3D.X() + sin(ToRad(Dinosaur3D.Angle())) * 15','Dinosaur3D.Y() - cos(ToRad(Dinosaur3D.Angle())) * 15'),depth+1)
  else:out+=event(inside,acts,depth)
# Rest bonuses are capped once per frame regardless of nearby building count.
out+=event(play+[nv('BuildMode')],[])+'> for each BuiltCampfire\n'+event([cmp('DistanceBetweenPositions(Player3D.X(),Player3D.Y(),BuiltCampfire.X(),BuiltCampfire.Y())','<','230')],[sv('BuildWarm',1)],2)
out+=event(play+[nv('BuildMode')],[])+'> for each BuiltShelter\n'+event([cmp('DistanceBetweenPositions(Player3D.X(),Player3D.Y(),BuiltShelter.X(),BuiltShelter.Y())','<','140')],[sv('BuildRest',1)],2)
out+=event(play+[nv('BuildWarm','=',1),nv('Threat','=',0)],[sv('Health',ex('min(100,Health+2*TimeDelta())')),sv('Stamina',ex('min(100,Stamina+5*TimeDelta())')),sv('Dirty',1)])
out+=event(play+[nv('BuildRest','=',1),nv('Threat','=',0)],[sv('Stamina',ex('min(100,Stamina+8*TimeDelta())')),sv('Dirty',1)])
out+=event(play+[nv('BuildMode')],[txt('BuildToggleLabel',q('B 建造 · 庇护所 / 栅栏 / 篝火'))])
out+=event(play+[nv('BuildWarm','=',1)],[txt('BuildToggleLabel',q('篝火温暖：恢复生命与体力 · B 建造'))])
out+=event(play+[nv('BuildRest','=',1)],[txt('BuildToggleLabel',q('庇护所休息：恢复体力 · B 建造'))])
out+=event(build,[f'do Show object={q(o)}' for o in ui]+[txt('BuildToggleLabel',q('B 退出建造 · Delete 拆除预览处建筑')),txt('BuildTitle',ex('"营地建造 · " + ToString(BuildCount) + " / 40   木 " + ToString(Wood) + " 石 " + ToString(Stone) + " 纤 " + ToString(Fiber)')),txt('BuildStatus',ex('BuildReason + NewLine() + "WASD 移位 · R 旋转 · Enter 建造" + NewLine() + "朝向 " + ToString(BuildAngle) + "° · Delete 拆除（返还一半）"')),'do Hide object="HarvestPanel"','do Hide object="HarvestHint"','do Hide object="HeldAxe"','do Hide object="CombatSpear"'])
for i in range(1,4):
 out+=event(build,[f'do ChangeColor object="BuildChoice{i}" tint="170;190;180"'])
 out+=event(build+[nv('BuildKind','=',i)],[f'do ChangeColor object="BuildChoice{i}" tint="255;215;125"'])
# Conceal the underlying companion card while the construction panel occupies it.
underlay=['DinoPanel','DinoName','DinoLevel','TrustText','TrustTrack','TrustMeter','Feed','FeedLabel','MountButton','MountLabel','AudioButton','AudioLabel']
out+=event(build,[f'do Hide object={q(o)}' for o in underlay])
out+=event(play+[nv('BuildMode')],[f'do Show object={q(o)}' for o in underlay])
# Depleted resource nodes stay dormant inside a building footprint.
out+=event([nv('Mode')],[])+'> for each Buildings\n>> for each HarvestNodes\n'+event([ov('HarvestNodes','Cooldown','>',0),cmp('abs(HarvestNodes.X()-Buildings.X())','<','Buildings.Variable(WorldHX)+50'),cmp('abs(HarvestNodes.Y()-Buildings.Y())','<','Buildings.Variable(WorldHY)+50')],[so('HarvestNodes','Cooldown',ex('max(1,HarvestNodes.Variable(Cooldown))'))],3)
out+=event([nv('Mode','>=',0)],[so('BuildStatus',k,ex(v)) for k,v in [('Mode','BuildMode'),('Kind','BuildKind'),('Valid','BuildValid'),('Count','BuildCount'),('X','BuildX'),('Y','BuildY'),('Angle','BuildAngle'),('Slot','BuildSlot'),('Warm','BuildWarm'),('Rest','BuildRest'),('Wood','Wood'),('Stone','Stone'),('Fiber','Fiber')]])
assert endmarker in s;s=s.replace(endmarker,out+endmarker,1)
s=s.replace('storage_name="JurassicWorldDemo"','storage_name=expr(SaveStorage)')
s=s.replace('按 Q 返回营地，再按 E 或快捷栏 7 加固。','按 B 开启建造，选 1 庇护所；移动到空地后按 Enter。').replace('回到木屋加固营地，为下一次出发建立落脚点。','收集材料，亲手搭建一座庇护所，为下一次出发建立落脚点。')
F.write_text(s.rstrip()+'\n',encoding='utf-8')
