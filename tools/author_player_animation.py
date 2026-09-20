"""Install native player animation events; safe to rerun for controller tuning."""
from pathlib import Path
import re
P=Path(__file__).resolve().parents[1]
f=P/'scenes/Game/functions/sceneUpdate.events';s=f.read_text(encoding='utf-8')
marker='@comment "Player skeletal animation controller"'
s=s.split(marker)[0].rstrip()+'\n'
def cond(v,op='=',val=0):return f'if NumberVariable variable="{v}" comparison_sign="{op}" value={val}'
def obj(v,op='=',val=0):return f'if NumberObjectVariable object="Player3D" variable="{v}" comparison_sign="{op}" value={val}'
def seto(v,val):return f'do SetNumberObjectVariable object="Player3D" variable="{v}" modification_sign="=" value={val}'
def event(cs,acts):return '\n'.join(cs+acts)+'\n\n'
playing=[cond('Mode'),cond('RenderMode','=',1),cond('Riding')]
# Reset sprint intent before input, preserve diagonal normalization and mounted speed.
s=s.replace('do SetNumberVariable variable="MoveSpeed" modification_sign="=" value=350','do SetNumberVariable variable="MoveSpeed" modification_sign="=" value=350\n'+seto('Sprinting',0)) if 'variable="Sprinting"' not in s else s
if '@comment "Sprint input"' not in s:
 at='if NumberVariable variable="Mode" comparison_sign="=" value=0\nif NumberVariable variable="RenderMode" comparison_sign="=" value=1\nif NumberVariable variable="Riding" comparison_sign="=" value=0\ndo SetX object="Player3D" modification_sign="+"'
 sprint='@comment "Sprint input" background=[90,150,180] text=[255,255,255]\n\n'+event(playing+[cond('Stamina','>',1),'if KeyFromTextPressed key_to_check="LShift"'],[seto('Sprinting',1),'do SetNumberVariable variable="MoveSpeed" modification_sign="*" value=expr(500 / 350)'])
 assert at in s;s=s.replace(at,sprint+at,1)
# Face actual world motion after camera-relative input instead of fixed compass headings.
for key,angle in [('w',180),('s',0),('a',270),('d',90)]:
 pattern=f'(if KeyFromTextPressed key_to_check="{key}"\ndo SetNumberVariable[^\n]+)\ndo SetAngle object="Player3D"[^\n]+'
 s=re.sub(pattern,r'\1',s)
# Bone attachment is the only owner of equipped tool transforms.
s='\n'.join(line for line in s.splitlines() if not (line.startswith('do ') and any(f'="{n}"' in line for n in ['HeldAxe','CombatSpear']) and any(line.startswith('do '+a+' ') for a in ['SetX','SetY','SetAngle','Scene3D::Base3DBehavior::SetRotationX'])))+'\n'
s=s.replace('value=0.4\n','value=expr(0.4 - Player3D.Variable(Sprinting) * 0.13)\n')
s=s.replace('ToString(Stamina)', 'ToString(round(Stamina))')
s=s.replace('WASD 移动 · E 采集','WASD 移动 · Shift 奔跑 · E 采集')
out=marker+' background=[95,155,180] text=[255,255,255]\n\n'
acts=[]
for tool in ['HeldAxe','CombatSpear']:
 acts += [f'do Model3DBoneAttachment::Model3DBoneAttachmentBehavior::AttachToModelBone parameter_3d_object="{tool}" bone_attachment_behavior="HandAttachment" target_3d_model="Player3D" bone_name="GripR"',f'do Model3DBoneAttachment::Model3DBoneAttachmentBehavior::SetBoneAttachmentRotationOffset parameter_3d_object="{tool}" bone_attachment_behavior="HandAttachment" x_rotation_offset=0 y_rotation_offset=0 z_rotation_offset=0']
out+=event(['if SceneJustBegins'],acts)
out+=event(playing,[seto('AnimationState',0),seto('Travel','expr(DistanceBetweenPositions(PreviousX, PreviousY, Player3D.X(), Player3D.Y()))'),'do AnimatableCapability::AnimatableBehavior::PlayAnimation object="Player3D" behavior="Animation"'])
move=playing+[obj('Travel','>',.1),cond('MoveSpeed','>',0),'if BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(MoveX) + abs(MoveY)) comparison_sign=">" second_expression=0']
out+=event(move,[seto('AnimationState',1)])
out+=event(move+[obj('Sprinting','=',1)],[seto('AnimationState',2),'do SetNumberVariable variable="Stamina" modification_sign="=" value=expr(max(0, Stamina - 12 * TimeDelta()))','do SetNumberVariable variable="Dirty" modification_sign="=" value=1'])
out+=event(playing+['if NumberObjectVariable object="HarvestNodes" variable="Target" comparison_sign="=" value=1','if NumberObjectVariable object="HarvestNodes" variable="Progress" comparison_sign=">" value=0'],[seto('AnimationState',3),'do SetAngle object="Player3D" modification_sign="=" angle_in_degrees=expr(AngleBetweenPositions(Player3D.X(), Player3D.Y(), HarvestNodes.X(), HarvestNodes.Y()) - 90)','do Hide object="HeldAxe"'])
for var,state in [('AxeSwing',4),('CombatSwing',5),('HitFlash',6)]:
 cs=playing+[cond(var,'>',0)]
 if var=='CombatSwing':cs+=[cond('Spear','>',0)]
 out+=event(cs,[seto('AnimationState',state)])
out+=event(playing+[obj('AnimationState','<=',2),obj('Travel','>',.1),'if BuiltinCommonInstructions::CompareNumbers first_expression=expr(abs(MoveX) + abs(MoveY)) comparison_sign=">" second_expression=0'],['do SetAngle object="Player3D" modification_sign="=" angle_in_degrees=expr(AngleBetweenPositions(PreviousX, PreviousY, Player3D.X(), Player3D.Y()) - 90)'])
out+=event([cond('Mode','=',7)],[seto('AnimationState',7),'do AnimatableCapability::AnimatableBehavior::PlayAnimation object="Player3D" behavior="Animation"'])
for i,clip in enumerate(['Idle','Walk','Run','Gather','Chop','Thrust','Hurt','Death']):
 out+=event([obj('AnimationState','=',i)], [f'do AnimatableCapability::AnimatableBehavior::SetName object="Player3D" behavior="Animation" modification_sign="=" animation_name="{clip}"'])
for cs in [[cond('Mode','>',0),cond('Mode','<',7)],[cond('Riding','=',1)],[cond('RenderMode','=',0)]]:
 out+=event(cs,['do AnimatableCapability::AnimatableBehavior::PauseAnimation object="Player3D" behavior="Animation"'])
out+=event([cond('RenderMode','=',1)],[seto('HandZ','expr(Player3D.BoneZ("GripR"))'),seto('FootZ','expr(Player3D.BoneZ("FootR"))'),seto('HandRX','expr(Player3D.BoneRotationX("GripR"))'),seto('AttachmentReady',0)])
out+=event(['if Model3DBoneAttachment::Model3DBoneAttachmentBehavior::IsBoneAttachmentResolved parameter_3d_object="HeldAxe" bone_attachment_behavior="HandAttachment"'],[seto('AttachmentReady',1)])
f.write_text((s+'\n'+out).rstrip()+'\n',encoding='utf-8')
