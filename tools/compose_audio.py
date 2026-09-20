"""Original procedural score and foley. No sampled/copyrighted music; deterministic PCM WAV."""
from pathlib import Path
import numpy as np, wave, json
P=Path(__file__).resolve().parents[1]/'assets/audio';P.mkdir(exist_ok=True)
SR=32000; rng=np.random.default_rng(920);manifest=[]
def write(name,x,loop=False):
 x=np.asarray(x);x=x[:,None] if x.ndim==1 else x
 if not loop:
  n=min(400,len(x)//4);x[:n]*=np.linspace(0,1,n)[:,None];x[-n:]*=np.linspace(1,0,n)[:,None]
 x=x/(max(1,np.max(np.abs(x))/.85));pcm=(x*32767).astype('<i2')
 with wave.open(str(P/(name+'.wav')),'wb') as w:w.setnchannels(x.shape[1]);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())
 manifest.append({'name':name+'.wav','seconds':round(len(x)/SR,3),'peak':float(np.max(np.abs(x))),'loop':loop})
def tone(freq,dur,style='pluck'):
 t=np.arange(int(dur*SR))/SR
 if style=='flute':return (.8*np.sin(2*np.pi*freq*t+.025*np.sin(2*np.pi*5*t))+.12*np.sin(2*np.pi*freq*2*t))*np.minimum(t/.12,1)*np.minimum((dur-t)/.25,1)*.20
 return (np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*freq*2.01*t)+.12*np.sin(2*np.pi*freq*3.98*t))*np.exp(-t*5/dur)*np.minimum(t/.006,1)*.2
def hz(n):return 440*2**((n-69)/12)
# 16 bars, 80 BPM, D minor pentatonic. Circular delays preserve all loop tails.
beat=.75;duration=48;N=int(duration*SR);score=np.zeros((N,2));danger=np.zeros((N,2))
def put(dst,at,x,gain=1,pan=0):
 ix=(np.arange(len(x))+int(at*SR))%len(dst)
 dst[ix,0]+=x*gain*np.sqrt((1-pan)/2);dst[ix,1]+=x*gain*np.sqrt((1+pan)/2)
roots=[50,46,53,48];motifs=[[74,77,81,79,77,74],[77,81,84,81,79,77],[72,77,79,81,77,74],[72,69,72,74,77,74]]
for bar in range(16):
 root=roots[(bar//2)%4];start=bar*4*beat
 for off,note in zip([0,.5,1.5,2,2.5,3.5],[root,root+7,root+12,root+15,root+12,root+7]):put(score,start+off*beat,tone(hz(note),1.8),.65,(-.35 if off%1==0 else .35))
 if bar%2==0:
  for off,note in zip([.5,1.5,3,4.5,5.5,6.5],motifs[(bar//2)%4]):put(score,start+off*beat,tone(hz(note),beat*.95,'flute'),.85,.1)
 for j in [0,2]:
  t=np.arange(int(.5*SR))/SR;drum=np.sin(2*np.pi*(70*t+20*.04*(1-np.exp(-t/.04))))*np.exp(-t*14)*.17
  put(score,start+j*beat,drum,.6);put(danger,start+j*beat,drum,1.6)
 for j in range(8):
  put(danger,start+j*beat/2,tone(hz(root-12+(7 if j%4==3 else 0)),.25),1.1,-.15 if j%2 else .15)
  t=np.arange(int(.12*SR))/SR;noise=rng.standard_normal(len(t));shaker=np.diff(noise,prepend=0)*np.exp(-t*45)*.025
  put(score,start+j*beat/2,shaker,.3,.55);put(danger,start+j*beat/2,shaker,1.4,-.55)
for dst in [score,danger]:
 dry=dst.copy()
 for sec,gain in [(.19,.12),(.37,.08),(.61,.045)]:dst+=np.roll(dry,int(sec*SR),axis=0)[:,::-1]*gain
write('island-dawn',score,True);write('predator-pulse',danger,True)
def noise(dur):return rng.standard_normal(int(dur*SR))
def impact(dur,freq=90):
 t=np.arange(int(dur*SR))/SR;n=noise(dur);n=np.convolve(n,np.ones(12)/12,'same')
 return (.5*np.sin(2*np.pi*freq*t)*np.exp(-t*24)+.25*n*np.exp(-t*17))
write('footstep',impact(.18,115));write('dino-step',impact(.30,54));write('hurt',impact(.35,68))
write('bite',impact(.35,130)+noise(.35)*np.exp(-np.arange(int(.35*SR))/SR*30)*.10)
for name,notes in [('ui-click',[76,81]),('pickup',[74,81,86]),('craft',[62,69,74,81]),('quest-complete',[74,77,81,86]),('feed',[65,69,74]),('mount',[50,57,62]),('death',[50,45,38]),('respawn',[62,69,74])]:
 out=np.zeros(int((len(notes)*.11+.6)*SR))
 for i,n in enumerate(notes):
  a=tone(hz(n),.55);ix=int(i*.11*SR);out[ix:ix+len(a)]+=a
 write(name,out)
t=np.arange(int(.55*SR))/SR
write('drink',(np.sin(2*np.pi*(500*t+20*np.sin(t*35)))+.2*noise(.55))*np.sin(np.pi*t/.55)**2*.15)
write('swing',noise(.30)*np.sin(np.linspace(0,np.pi,int(.30*SR)))**2*.12)
write('build',impact(.8,100)+np.roll(impact(.8,150),int(.24*SR))*.7)
for name,base,dur in [('raptor-call',140,1.1),('rex-roar',52,1.6),('herbivore-call',180,1.2)]:
 t=np.arange(int(dur*SR))/SR;phase=2*np.pi*(base*t+base*.25*dur/np.pi*np.sin(np.pi*t/dur));env=np.sin(np.pi*t/dur)**1.2
 x=(np.sin(phase)+.35*np.sin(phase*2)+.2*np.sin(phase*3)+.13*noise(dur))*(.8+.2*np.sin(t*55))*env*.3
 write(name,x)
(P/'audio-manifest.json').write_text(json.dumps({'title':'Island Dawn / 岛屿初曦','bpm':80,'key':'D minor pentatonic','composition':'Original synthesis: plucked wood, breathy flute, low hand drums; synchronized danger pulse stem','files':manifest},indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(manifest))
