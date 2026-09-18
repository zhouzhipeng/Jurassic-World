from pathlib import Path
import json
p=Path('scenes/Game/functions/sceneUpdate.events');s=p.read_text(encoding='utf-8')
def c(v,x,op='='):return f'if NumberVariable variable="{v}" comparison_sign="{op}" value={x}\n'
def n(v,x,op='='):return f'do SetNumberVariable variable="{v}" modification_sign="{op}" value={x}\n'
def pos(o,a,x):return f'do Set{a} object="{o}" modification_sign="=" value={x}\n'
def angle(o,x):return f'do SetAngle object="{o}" modification_sign="=" angle_in_degrees={x}\n'
def msg(t):return 'do SetStringVariable variable="NoticeMessage" modification_sign="=" value='+json.dumps(t,ensure_ascii=False)+'\n'+n('Dirty',1)
def ev(a,b):return a+b+'\n'
def tx(t):return 'do TextContainerCapability::TextContainerBehavior::SetValue object="MountLabel" behavior="Text" modification_sign="=" text='+json.dumps(t,ensure_ascii=False)+'\n'
# Existing walk controls keep their input calculations; only the owner of motion changes.
s=s.replace('if KeyFromTextReleased key_to_check="F3"\n','if KeyFromTextReleased key_to_check="F3"\n'+c('Riding',0),1)
s=s.replace('if NumberVariable variable="StationIndex" comparison_sign="=" value=0\nif BuiltinCommonInstructions::Once','if NumberVariable variable="StationIndex" comparison_sign="=" value=0\n'+c('Riding',0)+'if BuiltinCommonInstructions::Once',1)
s=s.replace('if NumberVariable variable="StationIndex" comparison_sign="=" value=1\nif BuiltinCommonInstructions::Once','if NumberVariable variable="StationIndex" comparison_sign="=" value=1\n'+c('Riding',0)+'if BuiltinCommonInstructions::Once',1)
s=s.replace('do SetX object="Player3D" modification_sign="+"',c('Riding',0)+'do SetX object="Player3D" modification_sign="+"',1)
for axis in ['X','Y']:s=s.replace('if NumberVariable variable="RenderMode" comparison_sign="=" value=1\nif Pos'+axis+' object="Player3D"',c('RenderMode',1)+c('Riding',0)+'if Pos'+axis+' object="Player3D"')
# Station 0 returns to the actual companion, rather than its former static location.
s=s.replace('do SetX object="Player3D" modification_sign="=" value=650\ndo SetY object="Player3D" modification_sign="=" value=150','do SetX object="Player3D" modification_sign="=" value=expr(Dinosaur3D.X())\ndo SetY object="Player3D" modification_sign="=" value=expr(Dinosaur3D.Y() + 550)',1)
a=s.index('@comment "Proximity harvesting:');b=s.index('if NumberVariable variable="InputMode" comparison_sign="=" value=0\nif KeyFromTextReleased key_to_check="e"',a)
s=s[:a]+s[a:b].replace(c('Mode',0),c('Mode',0)+c('Riding',0))+s[b:]
s=s.replace('if KeyFromTextReleased key_to_check="e"\nif NumberVariable variable="HarvestNear"','if KeyFromTextReleased key_to_check="e"\n'+c('Riding',0)+'if NumberVariable variable="HarvestNear"',1)
a=s.index('@comment "Equipped axe:');s=s[:a]+s[a:].replace(c('Mode',0),c('Mode',0)+c('Riding',0))
# Mounted players cannot teleport away, feed themselves, or build through their mount.
guard=ev(c('Action',1)+c('Riding',1),n('Action',0)+msg('请先按 X 下坐骑，再进行互动。'))+ev(c('Action',5)+c('Riding',1),n('Action',0)+msg('骑乘时用 WASD 移动；先下坐骑才能快速旅行。'))
s=s.replace(c('Action',1),guard+c('Action',1),1)
# Shared mount and foot separation pass, before gathering and cameras.
b='@comment "Mount state, safe side dismount, rotated capsule separation" background=[95,150,175] text=[255,255,255]\n\n'
b+=ev(c('Mode',0)+c('RenderMode',1),n('DinoPreviousX','expr(Dinosaur3D.X())')+n('DinoPreviousY','expr(Dinosaur3D.Y())')+n('DinoPreviousAngle','expr(Dinosaur3D.Angle())')+n('DinoMoving',0))
for trigger in ['if KeyFromTextReleased key_to_check="x"\n','if IsCursorOnObject object="MountButton" accurate_test_yes_by_default=false\nif MouseButtonFromTextReleased button_to_check="Left"\n']:
 b+=ev(c('Mode',0)+c('RenderMode',1)+trigger,n('MountRequest',1))
b+=ev(c('MountRequest',1)+c('Riding',0)+c('Trust',100,'<'),n('MountRequest',0)+msg('先用浆果把信任提升到 100，才能骑乘。'))
b+=ev(c('MountRequest',1)+c('Riding',0)+'if Distance object="Player3D" object_2="Dinosaur3D" distance=650\n',n('Riding',1)+n('MountRequest',0)+n('SelectedHotbar',0)+msg('已骑乘！WASD 移动，右键转动镜头，X 下坐骑。'))
b+=ev(c('MountRequest',1)+c('Riding',0),n('MountRequest',0)+msg('请靠近恐龙再按 X 骑乘。'))
b+=ev(c('MountRequest',1)+c('Riding',1),n('MountFound',0))
for sign in [1,-1]:
 test=c('MountRequest',1)+c('Riding',1)+c('MountFound',0)
 b+=ev(test,n('DropX',f'expr(Dinosaur3D.X() + cos(ToRad(Dinosaur3D.Angle())) * {240*sign})')+n('DropY',f'expr(Dinosaur3D.Y() + sin(ToRad(Dinosaur3D.Angle())) * {240*sign})')+n('DropAllowed',1))
 limits=[('DropX',-1450,'<'),('DropX',1450,'>'),('DropY',-1650,'<'),('DropY',1200,'>')]
 for v,x,op in limits:b+=ev(test+c(v,x,op),n('DropAllowed',0))
 b+=ev(test+c('DropX',-1310,'>')+c('DropX',-490,'<')+c('DropY',-1070,'>')+c('DropY',-320,'<'),n('DropAllowed',0))
 b+=ev(test+c('DropAllowed',1),n('Riding',0)+n('MountFound',1)+n('MountRequest',0)+pos('Player3D','X','expr(DropX)')+pos('Player3D','Y','expr(DropY)')+n('PreviousX','expr(DropX)')+n('PreviousY','expr(DropY)')+msg('已安全下坐骑。'))
b+=ev(c('MountRequest',1),n('MountRequest',0)+msg('两侧没有安全落脚点，请移动到空地再下坐骑。'))
active=c('Mode',0)+c('RenderMode',1)+c('Riding',1)
b+=ev(active,pos('Dinosaur3D','X','expr(Dinosaur3D.X() + (MoveX * cos(ToRad(CameraYaw)) + MoveY * sin(ToRad(CameraYaw))) * MoveSpeed * 1.4 * TimeDelta())')+pos('Dinosaur3D','Y','expr(Dinosaur3D.Y() + (MoveY * cos(ToRad(CameraYaw)) - MoveX * sin(ToRad(CameraYaw))) * MoveSpeed * 1.4 * TimeDelta())'))
b+=ev(active+c('MoveX',0,'!=')+'or NumberVariable variable="MoveY" comparison_sign="!=" value=0\n',angle('Dinosaur3D','expr(AngleBetweenPositions(DinoPreviousX, DinoPreviousY, Dinosaur3D.X(), Dinosaur3D.Y()) - 90)'))
rollback=pos('Dinosaur3D','X','expr(DinoPreviousX)')+pos('Dinosaur3D','Y','expr(DinoPreviousY)')+angle('Dinosaur3D','expr(DinoPreviousAngle)')
# Conservative mount clearance encloses head and tail at every orientation.
for axis,limit,op in [('X',-1070,'<'),('X',1070,'>'),('Y',-1270,'<'),('Y',820,'>')]:
 b+=ev(active+f'if Pos{axis} object="Dinosaur3D" comparison_sign="{op}" value={limit}\n',rollback)
b+=ev(active+'if PosX object="Dinosaur3D" comparison_sign=">" value=-1680\nif PosX object="Dinosaur3D" comparison_sign="<" value=-120\nif PosY object="Dinosaur3D" comparison_sign=">" value=-1440\nif PosY object="Dinosaur3D" comparison_sign="<" value=50\n',rollback)
b+=ev(active+c('DinoMoving',0)+ 'if CompareNumbers expression=expr(DistanceBetweenPositions(DinoPreviousX, DinoPreviousY, Dinosaur3D.X(), Dinosaur3D.Y())) comparison_sign=">" expression_2=0.01\n',n('DinoMoving',1))
# Foot collider: capsule in dinosaur local coordinates, including a player radius.
foot=c('RenderMode',1)+c('Riding',0)
b+=ev(foot,n('CapsuleX','expr((Player3D.X() - Dinosaur3D.X()) * cos(ToRad(Dinosaur3D.Angle())) + (Player3D.Y() - Dinosaur3D.Y()) * sin(ToRad(Dinosaur3D.Angle())))')+n('CapsuleY','expr(-(Player3D.X() - Dinosaur3D.X()) * sin(ToRad(Dinosaur3D.Angle())) + (Player3D.Y() - Dinosaur3D.Y()) * cos(ToRad(Dinosaur3D.Angle())))')+n('CapsuleNearestY','expr(clamp(CapsuleY, -330, 200))')+n('CapsuleDistance','expr(sqrt(CapsuleX * CapsuleX + (CapsuleY - CapsuleNearestY) * (CapsuleY - CapsuleNearestY)))'))
b+=ev(foot+c('CapsuleDistance',0.001,'<'),n('CapsuleX',170)+n('CapsuleY','expr(CapsuleNearestY)')+n('CapsuleDistance',170))
b+=ev(foot+c('CapsuleDistance',170,'<='),n('CapsuleX','expr(CapsuleX * 170 / CapsuleDistance)')+n('CapsuleY','expr(CapsuleNearestY + (CapsuleY - CapsuleNearestY) * 170 / CapsuleDistance)')+pos('Player3D','X','expr(Dinosaur3D.X() + CapsuleX * cos(ToRad(Dinosaur3D.Angle())) - CapsuleY * sin(ToRad(Dinosaur3D.Angle())))')+pos('Player3D','Y','expr(Dinosaur3D.Y() + CapsuleX * sin(ToRad(Dinosaur3D.Angle())) + CapsuleY * cos(ToRad(Dinosaur3D.Angle())))'))
b+=ev(c('Riding',1),pos('Player3D','X','expr(Dinosaur3D.X())')+pos('Player3D','Y','expr(Dinosaur3D.Y())')+angle('Player3D','expr(Dinosaur3D.Angle())')+'do Hide object="Player3D"\ndo Show object="MountedRider"\n'+pos('MountedRider','X','expr(Dinosaur3D.X() + sin(ToRad(Dinosaur3D.Angle())) * 15)')+pos('MountedRider','Y','expr(Dinosaur3D.Y() - cos(ToRad(Dinosaur3D.Angle())) * 15)')+angle('MountedRider','expr(Dinosaur3D.Angle())'))
b+=ev(c('Riding',0),'do Show object="Player3D"\ndo Hide object="MountedRider"\n')
b+=ev(c('Riding',1)+c('DinoMoving',1)+c('Mode',0),'do AnimatableCapability::AnimatableBehavior::SetName object="Dinosaur3D" behavior="Animation" modification_sign="=" animation_name="Walk"\ndo SetNumberObjectVariable object="Dinosaur3D" variable="AnimationState" modification_sign="=" value=1\n')
b+=ev(c('Riding',0)+'or NumberVariable variable="DinoMoving" comparison_sign="=" value=0\n','do AnimatableCapability::AnimatableBehavior::SetName object="Dinosaur3D" behavior="Animation" modification_sign="=" animation_name="Idle"\ndo SetNumberObjectVariable object="Dinosaur3D" variable="AnimationState" modification_sign="=" value=0\n')
b+=ev(c('Mode',0),'do AnimatableCapability::AnimatableBehavior::PlayAnimation object="Dinosaur3D" behavior="Animation"\n')
b+=ev(c('Mode',0,'!='),'do AnimatableCapability::AnimatableBehavior::PauseAnimation object="Dinosaur3D" behavior="Animation"\n')
b+=ev(c('Riding',0)+c('Trust',100,'<'),tx('X  驯服后可骑乘'))
b+=ev(c('Riding',0)+c('Trust',100,'>='),tx('X  靠近恐龙骑乘'))
b+=ev(c('Riding',1),tx('X  下坐骑'))
marker=c('Mode',0)+c('RenderMode',1)+n('CanFeed',0);s=s.replace(marker,b+marker,1)
# Camera follows the saddle rather than aiming under the dinosaur.
s=s.replace('120 + sin(ToRad(CameraPitch)) * CameraDistance','120 + Riding * 220 + sin(ToRad(CameraPitch)) * CameraDistance').replace('z_position=120 layer="World3D"','z_position=expr(120 + Riding * 220) layer="World3D"')
s=s.replace('WASD move   Hold E gather / interact','WASD move   X ride   Hold E gather / interact')
p.write_text(s,encoding='utf-8')
