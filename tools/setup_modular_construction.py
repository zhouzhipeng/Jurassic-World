"""One-shot additive authoring of modular construction source declarations."""
from pathlib import Path
import re,json,uuid,tomllib
P=Path(__file__).resolve().parents[1]; O=P/'scenes/Game/objects'; S=P/'scenes/Game/scene.settings'
def read(p):return p.read_text(encoding='utf-8')
def write(p,s):p.write_text(s,encoding='utf-8')
def nv(n,v):return f'[[variables]]\nname = "{n}"\ntype = "number"\nvalue = {v}\n\n'
assert not (O/'PartFoundation.settings').exists(),'Already migrated'
parts=[('Foundation',10,150,150,6,2,3),('Pillar',11,20,20,3,0,1),('Wall',12,150,14,4,0,2),('Doorframe',13,150,14,4,0,2),('Ceiling',14,150,150,5,0,3),('Door',15,78,12,3,0,1),('Stairs',16,120,152,6,0,3)]
manifest={x['name']:x for x in json.loads(read(P/'assets/models/modular-manifest.json'))}
order=max(tomllib.loads(read(p))['order'] for p in O.glob('*.settings'))+1
scene=read(S); resources=read(P/'resources.settings'); names=[]; ghosts=[]
for n,k,hx,hy,w,s,f in parts:
 for suffix in ['', 'Valid','Invalid']:
  obj='Part'+n+suffix; asset='modular-'+n.lower()+('-'+suffix.lower() if suffix else '')+'.glb'
  names.append(obj) if not suffix else ghosts.append(obj)
  text=read(O/'BuiltPalisade.settings'); text=re.sub(r'order = \d+',f'order = {order}',text,count=1);order+=1
  text=text.replace('name = "BuiltPalisade"',f'name = "{obj}"').replace('build-palisade.glb',asset)
  a=text.index('[[variables]]');b=text.index('[content]')
  vals=dict(Kind=k,Slot=-1,HX=hx,HY=hy,WorldHX=hx,WorldHY=hy,BaseZ=0,Level=0,Parent=-1,Open=0,BaseAngle=0,CostWood=w,CostStone=s,CostFiber=f)
  text=text[:a]+''.join(nv(n,v) for n,v in vals.items())+text[b:]
  for key,dim in zip(['width','height','depth'],manifest[n.lower()]['dimensions']):text=re.sub(rf'^{key} = .*',f'{key} = {dim*100:.5f}',text,flags=re.M)
  if suffix:text=text.replace('isCastingShadow = true','isCastingShadow = false')
  write(O/f'{obj}.settings',text)
  resources+=f'\n[[resources]]\nkind = "model3D"\nname = "{asset}"\nfile = "assets/models/{asset}"\nmetadata = ""\nuserAdded = true\n'
  if suffix:scene+=f'\n[[layout.instances]]\nid = "{uuid.uuid4()}"\nobject = "{obj}"\nlayer = "world3d"\nat = [0, 0, 0]\n'
scene=scene.replace('BuildGhosts = [','BuildGhosts = ['+', '.join(json.dumps(n) for n in ghosts)+', ')
scene=scene.replace('[objectGroups]','[objectGroups]\nModularParts = '+json.dumps(names)+'\nAllBuildings = '+json.dumps(names+['BuiltShelter','BuiltPalisade','BuiltCampfire']))
newvars=dict(BuildLevel=0,BuildZ=0,BuildParent=-1,BuildRawX=0,BuildRawY=0,BuildBlocked=0,BuildDeleteBlocked=0,BuildMessageTime=0,BuildSuccess=0,BuildPlacedKind=0,BuildFloorCount=0,BuildWallCount=0,BuildRoofCount=0,PlayerFloor=0,FloorTarget=0,FloorCandidate=0,DoorSlot=-1,DoorDistance=0,BuildCostWood=0,BuildCostStone=0,BuildCostFiber=0)
scene=scene.replace('[[variables]]',''.join(nv(n,v) for n,v in newvars.items())+'[[variables]]',1)
scene=re.sub(r'(name = "BuildKind"\ntype = "number"\nvalue = )\d+',r'\g<1>10',scene)
scene=scene.replace('[[variables]]\nname = "BuildReason"','[[variables]]\nname = "BuildMessage"\ntype = "string"\nvalue = ""\n\n[[variables]]\nname = "BuildReason"')
# Scene's layer id is preserved rather than inferred from its display name.
worldid=next(l['id'] for l in tomllib.loads(read(S))['layout']['layers'] if l['name']=='World3D')
scene=scene.replace('layer = "world3d"',f'layer = "{worldid}"');write(S,scene);write(P/'resources.settings',resources)
E=P/'scenes/Game/external-events/ModularConstruction';(E/'functions').mkdir(parents=True)
write(E/'external-events.settings','kind = "externalEvents"\nsettingsFormatVersion = 5\norder = 27\nname = "ModularConstruction"\n')
write(E/'functions/sceneUpdate.settings',read(P/'scenes/Game/functions/sceneUpdate.settings'))
write(E/'functions/sceneUpdate.events','@comment "Modular construction" background=[120,145,90] text=[255,255,255]\n')
L=P/'scenes/Game/external-layout/GameHUD.settings';layout=read(L)
labels=['1 地基  6木 2石 3纤','2 柱子  3木 1纤','3 墙体  4木 2纤','4 门框  4木 2纤','5 楼板  5木 3纤','6 木门  3木 1纤','7 楼梯  6木 3纤','8 篝火  3木 3石']
def changeinstance(text,obj,x,y,w,h):
 pattern=rf'(\[\[layout.instances\]\]\n(?:(?!\[\[layout.instances\]\]).)*?object = "{obj}"\n(?:(?!\[\[layout.instances\]\]).)*)'
 def sub(m):
  a=re.sub(r'at = \[.*?\]',f'at = [{x}, {y}, 0]',m[0]);return re.sub(r'size = \[.*?\]',f'size = [{w}, {h}]',a)
 return re.sub(pattern,sub,text,flags=re.S)
for i in range(1,9):
 x=1040+((i-1)%2)*265;y=380+((i-1)//2)*39
 for label in [False,True]:
  name=f'BuildChoice{"Label" if label else ""}{i}';template=O/f'BuildChoice{"Label" if label else ""}1.settings';p=O/f'{name}.settings'
  if i>3:
   text=read(template).replace('name = "'+template.stem+'"',f'name = "{name}"');text=re.sub(r'order = \d+',f'order = {order}',text,count=1);order+=1
   write(p,text)
   layout+=f'\n[[layout.instances]]\nid = "{uuid.uuid4()}"\nobject = "{name}"\nlayer = "hud"\nat = [{x+8 if label else x}, {y+10 if label else y}, 0]\nz_order = 100\nsize = [{245 if label else 255}, {28 if label else 35}]\nkeep_ratio = false\n'
  else:layout=changeinstance(layout,name,x+8 if label else x,y+10 if label else y,245 if label else 255,28 if label else 35)
  if label:
   text=read(p);text=re.sub(r'^text = .*',f'text = {json.dumps(labels[i-1],ensure_ascii=False)}',text,flags=re.M);text=text.replace('characterSize = 17','characterSize = 15');write(p,text)
layout=changeinstance(layout,'BuildStatus',1042,541,520,95);write(L,layout)
p=O/'BuildStatus.settings';s=read(p);s=s.replace('[content]',''.join(nv(n,0) for n in ['Z','Level','Parent','Blocked','Floor','Doors','Placed'])+'[content]');write(p,s)
print('Declared 7 parts, 14 ghosts, 8 HUD choices, native external event owner.')
