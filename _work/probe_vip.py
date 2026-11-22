# -*- coding: utf-8 -*-
"""用登录态批量探测每首歌可用的音质层级。"""
import json, requests, time

cookies = {c['name']: c['value'] for c in json.load(open('DownloadSongs/_work/cookies.json')) if 'qq.com' in c['domain']}
UIN = cookies.get('uin', '')
JAR = 'uin=%s; qm_keyst=%s; qqmusic_key=%s' % (UIN, cookies.get('qm_keyst', ''), cookies.get('qqmusic_key', ''))

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
    'Referer': 'https://y.qq.com/', 'Cookie': JAR,
})

rows = json.load(open('DownloadSongs/_work/manifest.json', encoding='utf-8'))
TIERS = ['flac', 'mp3_320', 'mp3_128', 'm4a_128']
PREFIX = {'flac': ('F000', '.flac'), 'mp3_320': ('M800', '.mp3'),
          'mp3_128': ('M500', '.mp3'), 'm4a_128': ('C400', '.m4a')}

res = {}
B = 10
for i in range(0, len(rows), B):
    batch = rows[i:i + B]
    fns, mids, types = [], [], []
    for r in batch:
        for t in TIERS:
            p, ext = PREFIX[t]
            fns.append('%s%s%s%s' % (p, r['mid'], r['mid'], ext))
            mids.append(r['mid'])
            types.append(0)
    p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
        "guid": "10000", "songmid": mids, "songtype": types, "filename": fns,
        "uin": UIN, "loginflag": 1, "platform": "20"}},
        "comm": {"uin": UIN, "format": "json", "ct": 24, "cv": 0}}
    try:
        d = s.post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20).json()
        info = d['req_0']['data']['midurlinfo']
        sip = [x for x in d['req_0']['data'].get('sip', []) if x]
    except Exception as e:
        print('fail batch', i, e, flush=True)
        continue
    for j, r in enumerate(batch):
        q = {}
        for k, t in enumerate(TIERS):
            idx = j * 4 + k
            ok = idx < len(info) and bool(info[idx].get('purl'))
            q[t] = bool(ok)
        res[r['mid']] = q
    if i % 100 == 0:
        print('probe', i, flush=True)
    time.sleep(0.15)

json.dump(res, open('DownloadSongs/_work/avail_vip.json', 'w'))
from collections import Counter
c = Counter()
for q in res.values():
    for t, v in q.items():
        if v:
            c[t] += 1
print('probed', len(res), dict(c))
print('nothing:', sum(1 for q in res.values() if not any(q.values())))
bad = [r['n'] for r in rows if not any(res.get(r['mid'], {}).values())]
print('unavailable n:', bad)
