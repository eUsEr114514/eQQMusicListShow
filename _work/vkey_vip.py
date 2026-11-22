# -*- coding: utf-8 -*-
import json, requests

cookies = {c['name']: c['value'] for c in json.load(open('DownloadSongs/_work/cookies.json')) if 'qq.com' in c['domain']}
uin = cookies.get('uin', '')
jar = 'uin=%s; qm_keyst=%s; qqmusic_key=%s' % (uin, cookies.get('qm_keyst', ''), cookies.get('qqmusic_key', ''))
s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
    'Referer': 'https://y.qq.com/', 'Cookie': jar,
})
mid = '004XzGsM308yjw'
fns = ['F000%s%s.flac' % (mid, mid), 'M800%s%s.mp3' % (mid, mid), 'M500%s%s.mp3' % (mid, mid),
       'C400%s%s.m4a' % (mid, mid), 'RS01%s%s.flac' % (mid, mid), 'AI00%s%s.flac' % (mid, mid)]
p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
    "guid": "10000", "songmid": [mid] * len(fns), "songtype": [0] * len(fns), "filename": fns,
    "uin": uin, "loginflag": 1, "platform": "20"}},
    "comm": {"uin": uin, "format": "json", "ct": 24, "cv": 0}}
r = s.post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20)
print(r.status_code)
d = r.json()
data = d.get('req_0', {}).get('data', {})
print('sip', data.get('sip'))
for m in data.get('midurlinfo', []):
    print(m['filename'][:40], 'purl=', (m.get('purl') or '')[:70], 'code=', m.get('result'))
