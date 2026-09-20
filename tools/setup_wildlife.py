"""One-time source scaffolding; refuses duplicate execution."""
from pathlib import Path
import json,uuid,re
P=Path(__file__).resolve().parents[1];O=P/'scenes/Game/objects';S=P/'scenes/Game/scene.settings';R=P/'resources.settings'
s=S.read_text(encoding='utf-8');assert 'name = "Health"' not in s
def var(k,v):return f'[[variables]]\nname = "{k}"\ntype = "number"\nvalue = {v}\n\n'
vs={'Health':100,'Dead':0,'Invulnerable':0,'Threat':0,'ThreatMix':0,'MusicStarted':0,'Muted':0,'StepClock':0,'CombatCD':0,'CombatSwing':0,'CombatHit':0,'Kills':0,'DeathCount':0,'NearestWild':9999,'HitFlash':0,'SafeCamp':0,'AudioMode':0,'AudioRiding':0,'SoundClock':0,'CombatLesson':0,'FacingTarget':0}
s=s.replace('[[variables]]', ''.join(var(k,v) for k,v in vs.items())+'[[variables]]',1)
s=s.replace('HarvestNodes = ', 'Wildlife = ["Triceratops", "Stegosaur", "Raptor", "Tyrannosaur"]\nPredators = ["Raptor", "Tyrannosaur"]\nHarvestNodes = ',1)
r=R.read_text(encoding='utf-8');order=232
def resource(kind,name,path):
 global r
 r+=f'\n[[resources]]\nkind = "{kind}"\nname = "{name}"\nfile = "{path}"\nmetadata = ""\nuserAdded = true\n'
def inst(name,x,y,layer='hud',w=None,h=None,z=0):
 global s
 s+=f'\n[[layout.instances]]\nid = "{uuid.uuid4()}"\nobject = "{name}"\nlayer = "{layer}"\nat = [{x}, {y}, {z}]\nz_order = {20 if layer=="hud" else 0}\n'
 if w:s+=f'size = [{w}, {h}]\nkeep_ratio = false\n'
meta=json.loads((P/'assets/models/wildlife-manifest.json').read_text())
config=[('Triceratops',-950,650,0,120,220,95,0),('Stegosaur',750,780,0,110,250,80,0),('Raptor',-100,-1100,1,95,190,285,12),('Tyrannosaur',850,-1200,1,170,340,210,24)]
for info,(name,x,y,carn,rad,half,speed,dmg) in zip(meta,config):
 f=info['species']+'.glb';resource('model3D',f,'assets/models/'+f)
 dims=[round(v*100) for v in info['dimensions']]
 obj=f'kind = "object"\nsettingsFormatVersion = 6\norder = {order}\nfolder = ["Wildlife"]\nname = "{name}"\ntype = "Scene3D::Model3DObject"\nbehaviors = [ ]\neffects = [ ]\n';order+=1
 ovs={'HP':100 if name=='Raptor' else 240,'MaxHP':100 if name=='Raptor' else 240,'Carnivore':carn,'HomeX':x,'HomeY':y,'Radius':rad,'HalfLength':half,'Speed':speed,'Damage':dmg,'State':0,'Clock':0,'AIClock':0,'Cooldown':2,'Windup':0,'DamageDone':0,'PX':x,'PY':y,'PA':0,'TargetX':x,'TargetY':y,'Distance':0,'Travel':0,'Respawn':0,'AnimationState':0,'LocalX':0,'LocalY':0,'NearY':0,'Separation':0,'BodyDistance':0}
 obj+=''.join(var(k,v) for k,v in ovs.items())
 obj+=f'[content]\nmodelResourceName = "{f}"\nwidth = {dims[0]}\nheight = {dims[1]}\ndepth = {dims[2]}\nkeepAspectRatio = true\nrotationX = 90\nrotationY = 0\nrotationZ = 0\noriginLocation = "ModelOrigin"\ncenterLocation = "ModelOrigin"\nmaterialType = "StandardWithoutMetalness"\nisCastingShadow = true\nisReceivingShadow = true\ncrossfadeDuration = 0.12\nsharedAnimationModelResources = [ ]\n'
 for clip in info['clips']:obj+=f'\n[[content.animations]]\nname = "{clip}"\nsource = "{clip}"\nsourceModelResourceName = ""\nloop = true\nuseRootMotion = false\n'
 (O/(name+'.settings')).write_text(obj,encoding='utf-8');inst(name,x,y,'world3d')
for f in sorted((P/'assets/audio').glob('*.wav')):resource('audio',f.name,'assets/audio/'+f.name)
def clone(old,name,x,y,w,h,text=None,layer='hud'):
 global order
 st=(O/(old+'.settings')).read_text(encoding='utf-8');st=re.sub(r'order = \d+',f'order = {order}',st,1);order+=1;st=st.replace(f'name = "{old}"',f'name = "{name}"',1)
 if text is not None:st=re.sub(r'^text = .*$',lambda m:'text = '+json.dumps(text,ensure_ascii=False),st,flags=re.M);st=st.replace('characterSize = 13','characterSize = 17')
 (O/(name+'.settings')).write_text(st,encoding='utf-8');inst(name,x,y,layer,w,h)
clone('NoticePanel','WildPanel',340,96,650,82)
clone('Value0','WildHint',358,108,615,70,'荒野生态 · 留意食肉恐龙\n空格反击 · M 声音 · 濒危时返回营地')
clone('MountButton','AudioButton',1050,588,310,36)
clone('Value0','AudioLabel',1066,596,290,30,'M 声音：开启')
clone('NoticePanel','DeathPanel',400,240,800,370)
clone('JournalInstruction','DeathText',440,295,720,260,'你倒下了\n\n按 Enter 在营地重生\n保留工具，损失少量食物')
# Full-screen translucent red hit feedback, behind text.
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><rect width="1600" height="900" fill="#a51f22" fill-opacity=".32"/></svg>'
(P/'assets/hit-flash.svg').write_text(svg);resource('image','hit-flash.svg','assets/hit-flash.svg')
clone('NoticePanel','DamageFlash',0,0,1600,900)
fp=O/'DamageFlash.settings';fp.write_text(fp.read_text().replace('NoticePanel.svg','hit-flash.svg'),encoding='utf-8')
S.write_text(s,encoding='utf-8');R.write_text(r,encoding='utf-8')
print('Registered 4 wildlife species, audio assets and combat UI')
