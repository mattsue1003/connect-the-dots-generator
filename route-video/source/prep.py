import json, math, urllib.request, io, os
from PIL import Image
d=json.load(open('osrm.json'))
r=d['routes'][0]
co=r['geometry']['coordinates']
def hav(a,b):
    R=6371000; la1,la2=math.radians(a[1]),math.radians(b[1]); dl=math.radians(b[0]-a[0]); dp=la2-la1
    h=math.sin(dp/2)**2+math.cos(la1)*math.cos(la2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))
cum=[0]
for i in range(1,len(co)): cum.append(cum[-1]+hav(co[i-1],co[i]))
# elevation from terrarium z13
Z=13; cache={}
def tile(x,y):
    k=(x,y)
    if k not in cache:
        p=f'tiles/{Z}_{x}_{y}.png'; os.makedirs('tiles',exist_ok=True)
        if not os.path.exists(p):
            urllib.request.urlretrieve(f'https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{Z}/{x}/{y}.png',p)
        cache[k]=Image.open(p).convert('RGB')
    return cache[k]
def elev(lon,lat):
    n=2**Z; x=(lon+180)/360*n; y=(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n
    im=tile(int(x),int(y)); px=min(255,int((x%1)*256)); py=min(255,int((y%1)*256))
    R,G,B=im.getpixel((px,py)); return R*256+G+B/256-32768
el=[round(elev(*c),1) for c in co]
# steps -> distance ranges, durations
steps=[];s=0;t=0
for st in r['legs'][0]['steps']:
    steps.append(dict(d0=s,d1=s+st['distance'],t0=t,t1=t+st['duration'],name=st.get('name',''),ref=st.get('ref','')))
    s+=st['distance'];t+=st['duration']
json.dump(dict(coords=co,cum=[round(c,1) for c in cum],elev=el,steps=steps,total=cum[-1],dur=r['duration']),open('route.json','w'))
print(len(co),cum[-1],min(el),max(el))
print(el[::15])
