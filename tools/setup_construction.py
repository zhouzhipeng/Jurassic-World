"""One-time native object/resource definitions for the construction kit."""
from pathlib import Path
if (Path(__file__).resolve().parents[1] / "extensions/JurassicActors").exists():
    raise SystemExit("This one-shot generator targets the pre-prefab layout. Edit scene external events and JurassicActors prefab sources directly.")
import json,uuid,re
P=Path(__file__).resolve().parents[1];S=P/'scenes/Game/scene.settings';R=P/'resources.settings';O=P/'scenes/Game/objects'
s=S.read_text(encoding='utf-8');r=R.read_text(encoding='utf-8');assert 'name = "BuildMode"' not in s
def var(n,v):return f'[[variables]]\nname = "{n}"\ntype = "number"\nvalue = {v}\n\n'
vs={'BuildMode':0,'BuildKind':1,'BuildAngle':0,'BuildX':0,'BuildY':0,'BuildHX':0,'BuildHY':0,'BuildWorldHX':0,'BuildWorldHY':0,'BuildValid':0,'BuildCount':0,'BuildSlot':-1,'BuildWood':10,'BuildStone':5,'BuildFiber':8,'BuildRestore':0,'BuildDeleteSlot':-1,'BuildDeleteDistance':9999,'BuildLX':0,'BuildLY':0,'BuildWarm':0,'BuildRest':0}
block=''.join(var(k,v) for k,v in vs.items())+'[[variables]]\nname = "BuildReason"\ntype = "string"\nvalue = ""\n\n[[variables]]\nname = "BuildJSON"\ntype = "string"\nvalue = "[]"\n\n[[variables]]\nname = "BuildingRecords"\ntype = "array"\nchildren = []\n\n'
s=s.replace('[[variables]]',block+'[[variables]]',1)
names=['BuiltShelter','BuiltPalisade','BuiltCampfire'];ghosts=[n+x for n in names for x in ['Valid','Invalid']]
s=s.replace('[objectGroups]','[objectGroups]\nBuildings = '+json.dumps(names)+'\nBuildGhosts = '+json.dumps(ghosts),1)
order=244
def resource(name):
 global r
 r+=f'\n[[resources]]\nkind = "model3D"\nname = "{name}"\nfile = "assets/models/{name}"\nmetadata = ""\nuserAdded = true\n'
def inst(n,x,y,z=0,layer='hud',w=None,h=None):
 global s
 s+=f'\n[[layout.instances]]\nid = "{uuid.uuid4()}"\nobject = "{n}"\nlayer = "{layer}"\nat = [{x}, {y}, {z}]\nz_order = 100\n'
 if w:s+=f'size = [{w}, {h}]\nkeep_ratio = false\n'
meta=json.loads((P/'assets/models/construction-manifest.json').read_text())
for kind,(n,info) in enumerate(zip(names,meta),1):
 for suffix,suffixfile in [('', ''),('Valid','-valid'),('Invalid','-invalid')]:
  name=n+suffix;asset='build-'+info['name']+suffixfile+'.glb';resource(asset)
  dims=[round(x*100,3) for x in info['dimensions']]
  st=f'kind = "object"\nsettingsFormatVersion = 6\norder = {order}\nfolder = ["Construction"]\nname = "{name}"\ntype = "Scene3D::Model3DObject"\nbehaviors = []\neffects = []\n';order+=1
  for k,v in {'Kind':kind,'Slot':-1,'HX':240 if kind==1 else 200 if kind==2 else 80,'HY':205 if kind==1 else 25 if kind==2 else 80,'WorldHX':0,'WorldHY':0}.items():st+=var(k,v)
  st+=f'[content]\nmodelResourceName = "{asset}"\nwidth = {dims[0]}\nheight = {dims[1]}\ndepth = {dims[2]}\nkeepAspectRatio = true\nrotationX = 90\nrotationY = 0\nrotationZ = 0\noriginLocation = "ModelOrigin"\ncenterLocation = "ModelOrigin"\nmaterialType = "StandardWithoutMetalness"\nisCastingShadow = '+str(not suffix).lower()+'\nisReceivingShadow = true\ncrossfadeDuration = 0.1\nanimations = []\nsharedAnimationModelResources = []\n'
  (O/(name+'.settings')).write_text(st,encoding='utf-8')
  if suffix:inst(name,0,0,0,'world3d')
def clone(old,n,x,y,w,h,text=None):
 global order
 st=(O/(old+'.settings')).read_text(encoding='utf-8');st=re.sub(r'order = \d+',f'order = {order}',st,1);order+=1;st=st.replace(f'name = "{old}"',f'name = "{n}"',1)
 if text is not None:st=re.sub(r'^text = .*$',lambda _: 'text = '+json.dumps(text,ensure_ascii=False),st,flags=re.M)
 (O/(n+'.settings')).write_text(st,encoding='utf-8');inst(n,x,y,layer='hud',w=w,h=h)
clone('NoticePanel','BuildToggle',1140,651,430,43)
clone('WildHint','BuildToggleLabel',1156,662,400,28,'B  建造营地')
clone('NoticePanel','BuildPanel',1020,315,560,325)
clone('WildHint','BuildTitle',1042,335,520,35,'营地建造 / 0 / 40')
for i,t in enumerate(['1  木制庇护所   10 木 / 5 石 / 8 纤维','2  木栅栏        4 木 / 2 纤维','3  篝火          3 木 / 3 石']):
 clone('NoticePanel','BuildChoice'+str(i+1),1040,383+i*48,520,41)
 clone('WildHint','BuildChoiceLabel'+str(i+1),1052,394+i*48,500,29,t)
clone('WildHint','BuildStatus',1042,540,520,90,'WASD 调整位置 · R 旋转\nEnter 建造 · B 退出')
p=O/'BuildStatus.settings';st=p.read_text(encoding='utf-8').replace('variables = [ ]','');st=st.replace('[content]',''.join(var(k,0) for k in ['Mode','Kind','Valid','Count','X','Y','Angle','Slot','Warm','Rest'])+'[content]');p.write_text(st,encoding='utf-8')
S.write_text(s,encoding='utf-8');R.write_text(r,encoding='utf-8')
