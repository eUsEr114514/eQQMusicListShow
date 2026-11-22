# -*- coding: utf-8 -*-
"""逐个测试 token 候选，找出能拿到 320k/FLAC purl 的那一个。"""
import json, requests

keys = json.load(open('client_keys.json'))
UIN = '316951535'
H = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
     'Referer': 'https://y.qq.com/'}
mid = '004XzGsM308yjw'
fns = ['F000%s%s.flac' % (mid, mid), 'M800%s%s.mp3' % (mid, mid)]

for k in keys:
    for uin in (UIN, '0'):
        s = requests.Session()
        s.headers.update(dict(H, Cookie='uin=%s; qm_keyst=%s; qqmusic_key=%s' % (uin, k, k)))
        p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
            "guid": "10000", "songmid": [mid] * 2, "songtype": [0, 0], "filename": fns,
            "uin": uin, "loginflag": 1, "platform": "20"}},
            "comm": {"uin": uin, "format": "json", "ct": 24, "cv": 0}}
        try:
            d = s.post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20).json()
            data = d['req_0']['data']
            res = [bool(x.get('purl')) for x in data.get('midurlinfo', [])]
            print('len=%d uin=%s -> flac/320 %s  msg=%s' % (len(k), uin, res, data.get('msg', '')[:40]))
        except Exception as e:
            print('len=%d uin=%s ERR %s' % (len(k), uin, str(e)[:60]))
