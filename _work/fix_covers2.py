# -*- coding: utf-8 -*-
"""用网易云图替换占位封面。"""
import json, os, time
import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
API = 'https://music-api.gdstudio.xyz/api.php'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
rows = {r['n']: r for r in json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))}
targets = [57, 62, 83, 98, 113, 145, 160, 183, 340, 406, 415, 439, 473, 511, 574, 596, 643, 688, 704, 707, 714, 739, 769, 780]
s = requests.Session()
s.headers.update({'User-Agent': UA})
done, fail = [], []
for n in targets:
    row = rows[n]
    dst = os.path.join(COVERS, row['file'] + '.jpg')
    ok = False
    for q in ('%s %s' % (row['name'], row['artists'][0] if row['artists'] else ''), row['name']):
        try:
            res = s.get(API, params={'types': 'search', 'source': 'netease', 'name': q, 'count': 3}, timeout=25).json()
        except Exception:
            time.sleep(2)
            continue
        if not isinstance(res, list):
            time.sleep(2)
            continue
        for c in res[:3]:
            pid = c.get('pic_id')
            if not pid:
                continue
            try:
                info = s.get(API, params={'types': 'pic', 'source': 'netease', 'id': pid, 'size': 500}, timeout=25).json()
                u = info.get('url')
                if not u:
                    continue
                rr = s.get(u, timeout=30)
                if rr.status_code == 200 and len(rr.content) > 8000:
                    open(dst, 'wb').write(rr.content)
                    ok = True
                    break
            except Exception:
                continue
        if ok:
            break
        time.sleep(1)
    (done if ok else fail).append(n)
    time.sleep(0.8)
print('fixed', len(done), done)
print('fail', len(fail), fail)
