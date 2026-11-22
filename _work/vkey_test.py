import json, requests
s = requests.Session()
s.headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
                  'Referer':'https://y.qq.com/'})
guid='10000'
for uin, label in [('0','guest')]:
    payload={"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{
        "guid":guid,"songmid":["004XzGsM308yjw","0016dkmo3KX5lH"],"songtype":[0,0],
        "uin":uin,"loginflag":1,"platform":"20"}},
        "comm":{"uin":uin,"format":"json","ct":24,"cv":0}}
    r=s.post('https://u.y.qq.com/cgi-bin/musicu.fcg',json=payload,timeout=15)
    print(label, r.status_code)
    print(json.dumps(r.json(),ensure_ascii=False)[:1200])
