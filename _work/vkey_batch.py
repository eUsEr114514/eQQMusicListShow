import json, requests
s=requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36','Referer':'https://y.qq.com/'})
sl=json.load(open('DownloadSongs/_work/playlist_raw.json',encoding='utf-8'))['cdlist'][0]['songlist']
mids=list(dict.fromkeys(x['songmid'] for x in sl))
res={}
B=10
for i in range(0,len(mids),B):
    batch=mids[i:i+B]
    fns=[]
    for mid in batch: fns+=[f'F000{mid}{mid}.flac',f'M800{mid}{mid}.mp3',f'M500{mid}{mid}.mp3',f'C400{mid}{mid}.m4a']
    p={"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"10000","songmid":[m for m in batch for _ in range(4)],"songtype":[0]*len(fns),"filename":fns,"uin":"0","loginflag":1,"platform":"20"}},"comm":{"uin":"0","format":"json","ct":24,"cv":0}}
    try:
        d=s.post('https://u.y.qq.com/cgi-bin/musicu.fcg',json=p,timeout=20).json()
        info=d['req_0']['data']['midurlinfo']
    except Exception as e:
        print('batch fail',i,e,flush=True); continue
    for j,mid in enumerate(batch):
        q={}
        for k,tier in enumerate(['flac','mp3_320','mp3_128','m4a_128']):
            idx=j*4+k
            q[tier]=bool(info[idx]['purl']) if idx<len(info) else False
        res[mid]=q
json.dump(res,open('DownloadSongs/_work/avail.json','w'))
from collections import Counter
c=Counter()
for q in res.values():
    for t,v in q.items():
        if v: c[t]+=1
print('unique mids',len(mids),'probed',len(res),'tiers',dict(c))
print('none playable',sum(1 for q in res.values() if not any(q.values())))
