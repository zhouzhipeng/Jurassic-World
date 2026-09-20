"""Native IfDo authoring. Run once against the retained whole-building source."""
from pathlib import Path
import re,json
P=Path(__file__).resolve().parents[1]; G=P/'scenes/Game'; core=G/'functions/sceneUpdate.events'
def read(p):return p.read_text(encoding='utf-8')
def write(p,s):p.write_text(s,encoding='utf-8')
def q(s):return json.dumps(s,ensure_ascii=False)
def v(n,val,op='='):return f'SetNumberVariable variable={q(n)} modification_sign={q(op)} value=expr({val})'
def t(n,s):return f'SetStringVariable variable={q(n)} modification_sign="=" value={q(s)}'
def ov(o,n,val):return f'SetNumberObjectVariable object={q(o)} variable={q(n)} modification_sign="=" value=expr({val})'
def c(n,op,val):return f'NumberVariable variable={q(n)} comparison_sign={q(op)} value=expr({val})'
def oc(o,n,op,val):return f'NumberObjectVariable object={q(o)} variable={q(n)} comparison_sign={q(op)} value=expr({val})'
def cmp(a,op,b):return f'BuiltinCommonInstructions::CompareNumbers first_expression=expr({a}) comparison_sign={q(op)} second_expression=expr({b})'
def pos(o,axis,val):return f'Set{axis} object={q(o)} modification_sign="=" value=expr({val})'
def z(o,val):return f'Scene3D::Base3DBehavior::SetZ parameter_3d_object={q(o)} behavior="Object3D" modification_sign="=" value=expr({val})'
def angle(o,val):return f'SetAngle object={q(o)} modification_sign="=" angle_in_degrees=expr({val})'
def key(k):return f'KeyFromTextReleased key_to_check={q(k)}'
def sound():return 'PlaySound audio_file_or_audio_resource_name="build.wav" repeat_the_sound=false volume=55 pitch_speed=1'
out=[]
def e(conditions,actions=(),d=0):
 pre='>'*d+' ' if d else ''
 out.extend(pre+'if '+x for x in conditions);out.extend(pre+'do '+x for x in actions);out.append('')
def line(s,d=0):out.append(('>'*d+' ' if d else '')+s)
play=[c('Mode','=',0),c('RenderMode','=',1)];foot=play+[c('Riding','=',0)];build=foot+[c('BuildMode','=',1)]
parts=[('PartFoundation',10,150,150,6,2,3),('PartPillar',11,20,20,3,0,1),('PartWall',12,150,14,4,0,2),('PartDoorframe',13,150,14,4,0,2),('PartCeiling',14,150,150,5,0,3),('PartDoor',15,78,12,3,0,1),('PartStairs',16,120,152,6,0,3),('BuiltCampfire',3,80,80,3,3,0)]
src=read(core)
assert '@comment "Construction placement' in src, 'Already migrated: edit the external events directly.'
start=src.index('@comment "Construction placement');end=src.index('@comment "Player skeletal animation')
old=src[start:end];assert 'repeat 40' in old
# Keep legacy models/kinds and their collision/rest behavior intact. V2 adds parts.
restore=old[old.index('if NumberVariable variable="BuildRestore"'):old.index('link external "HUDBuildSelection"')]
restore=restore.replace('Delete object="Buildings"','Delete object="AllBuildings"').replace('repeat 40','repeat 128')
cut=restore.index('if NumberVariable variable="BuildRestore" comparison_sign="=" value=1\ndo SetNumberVariable variable="BuildRestore" modification_sign="=" value=0')
out.append(restore[:cut])
for obj,k,hx,hy,w,s,f in parts[:-1]:
 r='BuildingRecords[i]'
 e([c(r+'.Kind','=',k)],[f'Create object_to_create="{obj}" x_position=expr({r}.X) y_position=expr({r}.Y) layer="World3D"',angle(obj,r+'.Angle'),z(obj,r+'.Z'),ov(obj,'Slot','i'),ov(obj,'BaseZ',r+'.Z'),ov(obj,'Level',r+'.Level'),ov(obj,'Parent',r+'.Parent'),ov(obj,'Open',r+'.Open'),ov(obj,'BaseAngle',r+'.Angle'),ov(obj,'WorldHX',f'abs(cos(ToRad({r}.Angle)))*{hx}+abs(sin(ToRad({r}.Angle)))*{hy}'),ov(obj,'WorldHY',f'abs(sin(ToRad({r}.Angle)))*{hx}+abs(cos(ToRad({r}.Angle)))*{hy}'),v('BuildCount',1,'+')],2)
out.append(restore[cut:])
line('link external "HUDBuildSelection"');out.append('')
e([c('Mode','>=',0)],[v('BuildMessageTime','max(0,BuildMessageTime-TimeDelta())'),v('BuildSuccess',0)])
e(build+[key('r')],[v('BuildAngle','mod(BuildAngle+90,360)')])
e(build+[key('PageUp')],[v('BuildLevel','min(2,BuildLevel+1)')])
e(build+[key('PageDown')],[v('BuildLevel','max(0,BuildLevel-1)')])
e(build,[v('BuildRawX','Player3D.X()-sin(ToRad(CameraYaw))*450'),v('BuildRawY','Player3D.Y()-cos(ToRad(CameraYaw))*450'),v('BuildX','round(BuildRawX/300)*300'),v('BuildY','round(BuildRawY/300)*300'),v('BuildZ','20+BuildLevel*300'),v('BuildParent',-1),v('BuildValid',1),v('BuildSlot',-1),t('BuildReason','吸附就绪 · Enter 放置')])
for obj,k,hx,hy,w,s,f in parts:
 e(build+[c('BuildKind','=',k)],[v('BuildWood',w),v('BuildStone',s),v('BuildFiber',f),v('BuildHX',hx),v('BuildHY',hy)])
for k in [10,3]:e(build+[c('BuildKind','=',k)],[v('BuildZ',0),v('BuildParent',-2)])
e(build+[c('BuildKind','=',14)],[v('BuildZ','320+BuildLevel*300')])
e(build+[c('BuildKind','=',11)],[v('BuildX','round((BuildRawX-150)/300)*300+150'),v('BuildY','round((BuildRawY-150)/300)*300+150')])
for k in [12,13,15]:
 e(build+[c('BuildKind','=',k),cmp('mod(BuildAngle,180)','=',0)],[v('BuildY','round((BuildRawY-150)/300)*300+150')])
 e(build+[c('BuildKind','=',k),cmp('mod(BuildAngle,180)','=',90)],[v('BuildX','round((BuildRawX-150)/300)*300+150')])
e(build,[v('BuildWorldHX','abs(cos(ToRad(BuildAngle)))*BuildHX+abs(sin(ToRad(BuildAngle)))*BuildHY'),v('BuildWorldHY','abs(sin(ToRad(BuildAngle)))*BuildHX+abs(cos(ToRad(BuildAngle)))*BuildHY')])
# Floor sockets support walls/posts/stairs. Roof sockets require a wall or column.
e(build);line('for each ModularParts',1)
e([oc('ModularParts','Kind','=',10),'OR_PLACEHOLDER'],[],2) if False else None
floorconds=[cmp('abs(BuildX-ModularParts.X())','<=',151),cmp('abs(BuildY-ModularParts.Y())','<=',151),oc('ModularParts','Level','=','BuildLevel')]
for pk in [10,14]:
 for k in [11,12,13,16]:
  cond=floorconds+[oc('ModularParts','Kind','=',pk),c('BuildKind','=',k)]
  if k==16:cond += [cmp('abs(BuildX-ModularParts.X())+abs(BuildY-ModularParts.Y())','<',1)]
  e(cond,[v('BuildParent','ModularParts.Variable(Slot)')],2)
for pk in [11,12,13]:e(floorconds+[oc('ModularParts','Kind','=',pk),c('BuildKind','=',14)],[v('BuildParent','ModularParts.Variable(Slot)')],2)
e([c('BuildKind','=',11),oc('ModularParts','Kind','=',11),oc('ModularParts','Level','=','BuildLevel-1'),cmp('abs(BuildX-ModularParts.X())+abs(BuildY-ModularParts.Y())','<',1)],[v('BuildParent','ModularParts.Variable(Slot)')],2)
e([c('BuildKind','=',15),oc('ModularParts','Kind','=',13),oc('ModularParts','Level','=','BuildLevel'),cmp('abs(BuildX-ModularParts.X())+abs(BuildY-ModularParts.Y())','<',1),cmp('mod(ModularParts.Angle(),180)','=','mod(BuildAngle,180)')],[v('BuildParent','ModularParts.Variable(Slot)')],2)
def invalid(conditions,message,d=0):e(conditions,[v('BuildValid',0),t('BuildReason',message)],d)
invalid(build+[c('BuildParent','=',-1)],'缺少支撑：墙/柱/楼梯接地板；楼板接墙/柱；木门接门框')
for k in [10,3]:invalid(build+[c('BuildKind','=',k),c('BuildLevel','>',0)],'地基和篝火请切回第 1 层（PageDown）')
# One slot for each socket, wall and doorway are mutually exclusive.
e(build);line('for each ModularParts',1)
same=[cmp('abs(BuildX-ModularParts.X())+abs(BuildY-ModularParts.Y())','<',1),oc('ModularParts','BaseZ','=','BuildZ')]
invalid(same+[oc('ModularParts','Kind','=','BuildKind')],'这个构件位置已被占用',2)
for a,b in [(12,13),(13,12)]:invalid(same+[c('BuildKind','=',a),oc('ModularParts','Kind','=',b)],'此边缘已有墙体或门框',2)
# Free slot and existing terrain/actor safeguards.
e(build);line('local i = 0',1);line('repeat 128 index=i',1)
e([c('BuildSlot','<',0),c('BuildingRecords[i].Kind','=',0)],[v('BuildSlot','i')],2)
safestart=old.index('if NumberVariable variable="Mode"',old.index('do SetNumberVariable variable="BuildWorldHY"'))
safeend=old.index('if NumberVariable variable="Mode"',old.index('value="恐龙占用此处，请保持距离"'))
safe=old[safestart:safeend].replace('40 个建筑','128 个构件')
out.append(safe)
# Prevent player entombment at its current height.
invalid(build+[c('BuildKind','!=',10),c('BuildKind','!=',14),cmp('abs(BuildZ-PlayerFloor)','<',180),cmp('abs(BuildX-Player3D.X())','<','BuildWorldHX+40'),cmp('abs(BuildY-Player3D.Y())','<','BuildWorldHY+40')],'此处会卡住角色，请退开再建造')
for obj,k,hx,hy,w,s,f in parts:
 for suffix,val in [('Valid',1),('Invalid',0)]:
  ghost=obj+suffix
  e(build+[c('BuildKind','=',k),c('BuildValid','=',val)],[pos(ghost,'X','BuildX'),pos(ghost,'Y','BuildY'),angle(ghost,'BuildAngle'),z(ghost,'BuildZ'),f'Show object="{ghost}"'])
 e(build+[key('Return'),c('BuildValid','=',1),c('BuildKind','=',k)],[f'Create object_to_create="{obj}" x_position=expr(BuildX) y_position=expr(BuildY) layer="World3D"',angle(obj,'BuildAngle'),z(obj,'BuildZ'),ov(obj,'Slot','BuildSlot'),ov(obj,'WorldHX','BuildWorldHX'),ov(obj,'WorldHY','BuildWorldHY')]+([ov(obj,'BaseZ','BuildZ'),ov(obj,'Level','BuildLevel+1' if k==14 else 'BuildLevel'),ov(obj,'Parent','BuildParent'),ov(obj,'BaseAngle','BuildAngle')] if k>=10 else [])+[v('BuildSuccess',1)])
e(build+[c('BuildSuccess','=',1)],[v('BuildingRecords[BuildSlot].'+n,val) for n,val in [('Kind','BuildKind'),('X','BuildX'),('Y','BuildY'),('Z','BuildZ'),('Angle','BuildAngle'),('Level','BuildLevel'),('Parent','BuildParent'),('Open',0)]]+[v('Wood','BuildWood','-'),v('Stone','BuildStone','-'),v('Fiber','BuildFiber','-'),v('BuildCount',1,'+'),v('BuildPlacedKind','BuildKind'),v('BuildValid',0),v('Dirty',1),v('BuildMessageTime',2.5),t('BuildMessage','已搭建 · 继续拼接相邻构件'),sound()])
e(build+[c('BuildSuccess','=',1),c('BuildKind','=',14)],[v('BuildingRecords[BuildSlot].Level','BuildLevel+1')])
e(build+[key('Return'),c('BuildSuccess','=',0)],[v('BuildMessageTime',2.5),'SetStringVariable variable="BuildMessage" modification_sign="=" value=expr(BuildReason)'])
# Demolish the selected kind at the preview socket, never destroy supports first.
e(build,[v('BuildDeleteSlot',-1),v('BuildDeleteDistance',200),v('BuildDeleteBlocked',0)])
e(build);line('for each AllBuildings',1)
e([oc('AllBuildings','Kind','=','BuildKind'),cmp('DistanceBetweenPositions(BuildX,BuildY,AllBuildings.X(),AllBuildings.Y())','<','BuildDeleteDistance')]+[],[v('BuildDeleteSlot','AllBuildings.Variable(Slot)'),v('BuildDeleteDistance','DistanceBetweenPositions(BuildX,BuildY,AllBuildings.X(),AllBuildings.Y())')],2)
# Constrain modular deletion to the selected elevation (legacy remains ground).
e(build+[c('BuildDeleteSlot','>=',0),c('BuildKind','>=',10),cmp('abs(BuildingRecords[BuildDeleteSlot].Z-BuildZ)','>',1)],[v('BuildDeleteSlot',-1)])
e(build+[c('BuildDeleteSlot','>=',0)]);line('for each ModularParts',1)
e([oc('ModularParts','Parent','=','BuildDeleteSlot')],[v('BuildDeleteBlocked',1)],2)
e(build+[key('Delete'),c('BuildDeleteSlot','>=',0),c('BuildDeleteBlocked','=',1)],[v('BuildMessageTime',3),t('BuildMessage','仍在承重：请先拆门、楼板或上方构件')])
e(build+[key('Delete'),c('BuildDeleteSlot','>=',0),c('BuildDeleteBlocked','=',0),oc('AllBuildings','Slot','=','BuildDeleteSlot')],[v('BuildingRecords[BuildDeleteSlot].Kind',0),'Delete object="AllBuildings"',v('BuildCount',1,'-'),v('Wood','floor(BuildWood/2)','+'),v('Stone','floor(BuildStone/2)','+'),v('Fiber','floor(BuildFiber/2)','+'),v('BuildMessageTime',3),v('Dirty',1),t('BuildMessage','已拆除选中构件 · 返还一半材料'),sound()])
# Nearest door interaction outside construction; base record remains the socket.
e(foot,[v('DoorSlot',-1),v('DoorDistance',210)])
e(foot+[c('BuildMode','=',0)]);line('for each PartDoor',1)
e([cmp('abs(PartDoor.Variable(BaseZ)-PlayerFloor)','<',100),cmp('DistanceBetweenPositions(Player3D.X(),Player3D.Y(),PartDoor.X(),PartDoor.Y())','<','DoorDistance')],[v('DoorDistance','DistanceBetweenPositions(Player3D.X(),Player3D.Y(),PartDoor.X(),PartDoor.Y())'),v('DoorSlot','PartDoor.Variable(Slot)')],2)
e(foot+[c('BuildMode','=',0),key('e'),c('DoorSlot','>=',0),oc('PartDoor','Slot','=','DoorSlot')],[ov('PartDoor','Open','1-PartDoor.Variable(Open)'),v('BuildingRecords[DoorSlot].Open','PartDoor.Variable(Open)'),sound()])
e(play);line('for each PartDoor',1)
e([oc('PartDoor','Slot','>=',0)],[angle('PartDoor','PartDoor.Variable(BaseAngle)+PartDoor.Variable(Open)*90'),pos('PartDoor','X','BuildingRecords[PartDoor.Variable(Slot)].X+PartDoor.Variable(Open)*(-78*cos(ToRad(PartDoor.Variable(BaseAngle)))-78*sin(ToRad(PartDoor.Variable(BaseAngle))))'),pos('PartDoor','Y','BuildingRecords[PartDoor.Variable(Slot)].Y+PartDoor.Variable(Open)*(-78*sin(ToRad(PartDoor.Variable(BaseAngle)))+78*cos(ToRad(PartDoor.Variable(BaseAngle))))')],2)
# Walkable decks, ramps and gravity. Ground can step onto 20-unit foundations.
e(foot,[v('FloorTarget',0)])
e(foot);line('for each ModularParts',1)
for k in [10,14]:
 top='20' if k==10 else 'ModularParts.Variable(BaseZ)'
 e([oc('ModularParts','Kind','=',k),cmp('abs(Player3D.X()-ModularParts.X())','<=',150),cmp('abs(Player3D.Y()-ModularParts.Y())','<=',150),cmp(top,'<=','PlayerFloor+30'),cmp(top,'>','FloorTarget')],[v('FloorTarget',top)],2)
e(foot);line('for each PartStairs',1)
e([oc('PartStairs','Kind','=',16)],[v('BuildLX','(Player3D.X()-PartStairs.X())*cos(ToRad(PartStairs.Angle()))+(Player3D.Y()-PartStairs.Y())*sin(ToRad(PartStairs.Angle()))'),v('BuildLY','-(Player3D.X()-PartStairs.X())*sin(ToRad(PartStairs.Angle()))+(Player3D.Y()-PartStairs.Y())*cos(ToRad(PartStairs.Angle()))'),v('FloorCandidate','PartStairs.Variable(BaseZ)+clamp(150-BuildLY,0,300)')],2)
e([cmp('abs(BuildLX)','<',105),cmp('abs(BuildLY)','<=',160),cmp('abs(FloorCandidate-PlayerFloor)','<',40),cmp('FloorCandidate','>','FloorTarget')],[v('FloorTarget','FloorCandidate')],3)
e(foot,[v('PlayerFloor','max(FloorTarget,PlayerFloor-550*TimeDelta())'),z('Player3D','PlayerFloor')])
e(play+[c('Riding','=',1)],[v('PlayerFloor',0),z('Player3D',0)])
# Walls/columns block the survivor; frame leaves a clear doorway. Open doors
# swing to a hinge; collision uses the closed socket only while closed.
e(foot);line('for each ModularParts',1)
e([oc('ModularParts','Kind','!=',10),oc('ModularParts','Kind','!=',14),oc('ModularParts','Kind','!=',16),cmp('PlayerFloor','<','ModularParts.Variable(BaseZ)+285'),cmp('PlayerFloor+180','>','ModularParts.Variable(BaseZ)'),cmp('abs(Player3D.X()-ModularParts.X())','<','ModularParts.Variable(WorldHX)+32'),cmp('abs(Player3D.Y()-ModularParts.Y())','<','ModularParts.Variable(WorldHY)+32')],[v('BuildBlocked',1),v('BuildLX','(Player3D.X()-ModularParts.X())*cos(ToRad(ModularParts.Angle()))+(Player3D.Y()-ModularParts.Y())*sin(ToRad(ModularParts.Angle()))')],2)
e([oc('ModularParts','Kind','=',13),cmp('abs(BuildLX)','<',50)],[v('BuildBlocked',0)],3)
e([oc('ModularParts','Kind','=',15),oc('ModularParts','Open','=',1)],[v('BuildBlocked',0)],3)
e([c('BuildBlocked','=',1)],[pos('Player3D','X','PreviousX'),pos('Player3D','Y','PreviousY')],3)
# Ground-based dinosaur collision never treats a flat deck as a solid box.
e(play);line('for each ModularParts',1)
e([oc('ModularParts','Kind','!=',10),oc('ModularParts','Kind','!=',14),oc('ModularParts','BaseZ','<',300)],[],2)
padx='150+abs(sin(ToRad(Dinosaur3D.Angle())))*260';pady='150+abs(cos(ToRad(Dinosaur3D.Angle())))*260'
e([cmp('abs(Dinosaur3D.X()-ModularParts.X())','<',f'ModularParts.Variable(WorldHX)+{padx}'),cmp('abs(Dinosaur3D.Y()-ModularParts.Y())','<',f'ModularParts.Variable(WorldHY)+{pady}')],[pos('Dinosaur3D','X','DinoPreviousX'),pos('Dinosaur3D','Y','DinoPreviousY'),ov('Dinosaur3D','AnimationState',0)],3)
e([c('Riding','=',1)],[pos('Player3D','X','Dinosaur3D.X()'),pos('Player3D','Y','Dinosaur3D.Y()')],4)
line('for each Wildlife',3)
e([cmp('abs(Wildlife.X()-ModularParts.X())','<','ModularParts.Variable(WorldHX)+Wildlife.Variable(Radius)+abs(sin(ToRad(Wildlife.Angle())))*Wildlife.Variable(HalfLength)'),cmp('abs(Wildlife.Y()-ModularParts.Y())','<','ModularParts.Variable(WorldHY)+Wildlife.Variable(Radius)+abs(cos(ToRad(Wildlife.Angle())))*Wildlife.Variable(HalfLength)')],[pos('Wildlife','X','Wildlife.Variable(PX)'),pos('Wildlife','Y','Wildlife.Variable(PY)'),ov('Wildlife','AnimationState',0)],4)
# Shelter quest counts actual assembled parts, and overhead decks give rest.
e(play,[v('BuildFloorCount',0),v('BuildWallCount',0),v('BuildRoofCount',0)])
e(play);line('for each ModularParts',1)
for k,n in [(10,'BuildFloorCount'),(12,'BuildWallCount'),(13,'BuildWallCount'),(14,'BuildRoofCount')]:e([oc('ModularParts','Kind','=',k)],[v(n,1,'+')],2)
e([oc('ModularParts','Kind','=',14),cmp('abs(Player3D.X()-ModularParts.X())','<',140),cmp('abs(Player3D.Y()-ModularParts.Y())','<',140),cmp('ModularParts.Variable(BaseZ)-PlayerFloor','>',180),cmp('ModularParts.Variable(BaseZ)-PlayerFloor','<',350)],[v('BuildRest',1)],2)
e(play+[c('BuildFloorCount','>=',1),c('BuildWallCount','>=',3),c('BuildRoofCount','>=',1)],[v('Built',1)])
# Legacy body retains unchanged collisions/rest; HUD remains in its own modules.
collision=old.rfind('if NumberVariable variable="Mode"',0,old.index('> for each Buildings\n>> if BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(Player3D.X()'))
legacy=old[collision:]
# rfind above lands at the start of the full condition group (only Mode line).
legacy=legacy.replace('> for each Buildings\n>> for each HarvestNodes','> for each AllBuildings\n>> for each HarvestNodes').replace('HarvestNodes.X()-Buildings.X()','HarvestNodes.X()-AllBuildings.X()').replace('HarvestNodes.Y()-Buildings.Y()','HarvestNodes.Y()-AllBuildings.Y()').replace('expr(Buildings.Variable(WorldHX)+50)','expr(AllBuildings.Variable(WorldHX)+50)').replace('expr(Buildings.Variable(WorldHY)+50)','expr(AllBuildings.Variable(WorldHY)+50)')
out.append(legacy)
write(G/'external-events/ModularConstruction/functions/sceneUpdate.events','\n'.join(out)+'\n')
src=src[:start]+'link external "ModularConstruction"\n\n'+src[end:]
src=src.replace('variable="BuildKind" modification_sign="=" value=1','variable="BuildKind" modification_sign="=" value=10')
marker='if NumberVariable variable="Action" comparison_sign="=" value=10\nif GroupExists storage_name=expr(SaveStorage) group="BuildingsV1"\ndo ReadStringFromStorage storage_name=expr(SaveStorage) group="BuildingsV1" variable="BuildJSON"'
src=src.replace(marker,marker+'\n\nif NumberVariable variable="Action" comparison_sign="=" value=10\nif GroupExists storage_name=expr(SaveStorage) group="BuildingsV2"\ndo ReadStringFromStorage storage_name=expr(SaveStorage) group="BuildingsV2" variable="BuildJSON"')
write(core,src)
p=G/'external-events/HUDInventoryAndSave/functions/sceneUpdate.events';write(p,read(p).replace('group="BuildingsV1"','group="BuildingsV2"'))
# Rewrite only building UI selection/presentation and preserve HUD ownership.
out=[]
e([c('Mode','>=',0)],['Hide object="BuildGhosts"']+[f'Hide object="{n}"' for n in ['BuildPanel','BuildTitle','BuildStatus']+[f'BuildChoice{s}{i}' for i in range(1,9) for s in ['','Label']]]+[v('BuildWarm',0),v('BuildRest',0)])
e(foot,['Show object="BuildToggle"','Show object="BuildToggleLabel"'])
e([c('Mode','!=',0)],['Hide object="BuildToggle"','Hide object="BuildToggleLabel"'])
for i,(_,kind,*_) in enumerate(parts,1):
 for condition in [key('Num'+str(i)),f'IsCursorOnObject object="BuildChoice{i}" accurate_test_yes_by_default=false\nif MouseButtonFromTextReleased button_to_check="Left"']:
  e(build+[condition],[v('BuildKind',kind)])
write(G/'external-events/HUDBuildSelection/functions/sceneUpdate.events','\n'.join(out)+'\n')
out=[]
def txt(obj,expression):return f'TextContainerCapability::TextContainerBehavior::SetValue object="{obj}" behavior="Text" modification_sign="=" text=expr({expression})'
e(foot+[c('BuildMode','=',0)],[txt('BuildToggleLabel',q('B 建造 · 地基 / 墙 / 柱 / 楼板'))])
e(foot+[c('BuildMode','=',0),c('DoorSlot','>=',0)],[txt('BuildToggleLabel',q('E 打开 / 关闭木门 · B 建造'))])
e(build,[f'Show object="{n}"' for n in ['BuildPanel','BuildTitle','BuildStatus']+[f'BuildChoice{s}{i}' for i in range(1,9) for s in ['','Label']]]+[txt('BuildToggleLabel',q('B 退出 · Delete 拆除所选类型构件')),txt('BuildTitle','"木制构件 · " + ToString(BuildCount) + "/128   木"+ToString(Wood)+" 石"+ToString(Stone)+" 纤"+ToString(Fiber)'),txt('BuildStatus','BuildReason+NewLine()+"WASD 移位 · R 转向 · Enter 放置"+NewLine()+"PgUp/PgDn 楼层："+ToString(BuildLevel+1)+" · 绿色可搭 / 红色不可搭"'),'Hide object="HarvestPanel"','Hide object="HarvestHint"',ov('Player3D','HeldAxeVisible',0),ov('Player3D','CombatSpearVisible',0)])
e(build+[c('BuildMessageTime','>',0)],[txt('BuildStatus','BuildMessage+NewLine()+"WASD 移位 · R 转向 · Enter 放置"+NewLine()+"PgUp/PgDn 楼层："+ToString(BuildLevel+1)+" · Delete 拆除"')])
for i,(_,kind,*_) in enumerate(parts,1):
 e(build,[f'ChangeColor object="BuildChoice{i}" tint="170;190;180"'])
 e(build+[c('BuildKind','=',kind)],[f'ChangeColor object="BuildChoice{i}" tint="255;215;125"'])
for mode,verb in [(1,'Hide'),(0,'Show')]:e(foot+[c('BuildMode','=',mode)],[f'{verb} object="{n}"' for n in ['DinoPanel','DinoName','DinoLevel','TrustText','TrustTrack','TrustMeter','Feed','FeedLabel','MountButton','MountLabel','AudioButton','AudioLabel']])
write(G/'external-events/HUDBuildPresentation/functions/sceneUpdate.events','\n'.join(out)+'\n')
p=G/'external-events/HUDBuildStatus/functions/sceneUpdate.events';s=read(p).rstrip()+'\n'+''.join('do '+ov('BuildStatus',a,b)+'\n' for a,b in [('Z','BuildZ'),('Level','BuildLevel'),('Parent','BuildParent'),('Blocked','BuildDeleteBlocked'),('Floor','PlayerFloor'),('Doors','DoorSlot'),('Placed','BuildPlacedKind')]);write(p,s)
p=G/'external-events/HUDQuests/functions/sceneUpdate.events';s=read(p).replace('120 + Riding * 220','120 + PlayerFloor + Riding * 220')
s=s.replace('"建造庇护所  " + ToString(min(Built, 1)) + " / 1"','"地基 " + ToString(min(BuildFloorCount,1)) + "/1 · 墙/门框 " + ToString(min(BuildWallCount,3)) + "/3 · 楼板 " + ToString(min(BuildRoofCount,1)) + "/1"')
s=s.replace('按 B 开启建造，选 1 庇护所；移动到空地后按 Enter。','B 建造：1 铺地基 → 3 墙 / 4 门框 → 5 顶部楼板。').replace('需要木材 10、石头 5、纤维 8。','每件按 Enter 搭建；R 换边，6 安门，7 楼梯，PgUp 搭楼上。');write(p,s)
print('Authored modular sockets, support graph, floors, doors, persistence and HUD.')
