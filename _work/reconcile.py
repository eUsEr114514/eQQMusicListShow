# -*- coding: utf-8 -*-
"""按磁盘实际文件重建下载状态（校验时长/体积），并列出仍缺失的曲目。"""
import json, os, re
import mutagen

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
LIMIT = 25 * 1024 * 1024
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
status = {}

files = os.listdir(FILES)
byn = {}
for f in files:
    m = re.match(r'^(\d+)-', f)
    if m:
        byn.setdefault(int(m.group(1)), []).append(f)

bad = []
for row in rows:
    n = row['n']
    cand = byn.get(n, [])
    if not cand:
        continue
    f = os.path.join(FILES, cand[0])
    size = os.path.getsize(f)
    try:
        info = mutagen.File(f).info
        dur = float(info.length)
    except Exception:
        dur = 0
    ok = size <= LIMIT and dur and row['interval'] and abs(dur - row['interval']) <= 15
    if ok:
        status[str(n)] = {'ok': True, 'result': 'file:%s' % os.path.splitext(f)[1][1:],
                          'file': row['file'], 'bytes': size, 'dur': round(dur, 1)}
    else:
        bad.append((n, cand[0], size, round(dur, 1), row['interval']))

json.dump(status, open(os.path.join(WORK, 'dl_status.json'), 'w'), ensure_ascii=False)
print('verified ok', len(status), '/', len(rows))
missing = [r['n'] for r in rows if str(r['n']) not in status]
print('missing count', len(missing))
print('missing', missing)
print('bad files', len(bad), bad[:10])
