import json, requests
s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36','Referer':'https://y.qq.com/'})
mid='004XzGsM308yjw'
fns=[f'F000{mid}{mid}.flac', f'M800{mid}{mid}.mp3', f'M500{mid}{mid}.mp3', f'C400{mid}{mid}.m4a', f'RS01{mid}{mid}.flac']
payload={"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{
    "guid":"10000","songmid":[mid]*len(fns),"songtype":[0]*len(fns),"filename":fns,
    "uin":"0","loginflag":1,"platform":"20"}},
    "comm":{"uin":"0","format":"json","ct":24,"cv":0}}
r=s.post('https://u.y.qq.com/cgi-bin/musicu.fcg',json=payload,timeout=15)
d=r.json()['req_0']['data']
for m in d['midurlinfo']:
    print(m['filename'], '|', 'purl=', (m['purl'] or '')[:80], '| errtype=', m.get('errtype'), '| code=', m.get('result'))
