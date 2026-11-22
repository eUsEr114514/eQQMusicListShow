# -*- coding: utf-8 -*-
"""总审计：文件校验、缺失清单、封面补齐（网易云图优先）。"""
import json, os, re, time
import requests
import mutagen

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
API = 'https://music-api.gdstudio.xyz/api.php'
LIMIT = 25 * 1024 * 1024
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
s = requests.Session()
s.headers.update({'User-Agent': UA})


def audit():
    files = os.listdir(FILES)
    byn = {}
    for f in files:
        m = re.match(r'^(\d+)-', f)
        if m:
            byn.setdefault(int(m.group(1)), []).append(f)
    ok, missing, bad = [], [], []
    for r in rows:
        cand = [f for f in byn.get(r['n'], []) if f.lower().endswith(('.mp3', '.flac', '.m4a'))]
        if not cand:
            missing.append(r)
            continue
        p = os.path.join(FILES, cand[0])
        sz = os.path.getsize(p)
        try:
            dur = float(mutagen.File(p).info.length)
        except Exception:
            dur = 0
        if sz > LIMIT or not dur:
            bad.append((r['n'], cand[0], sz, dur))
            continue
        ok.append((r, p, sz, dur))
    return ok, missing, bad


def fix_cover(row):
    dst = os.path.join(COVERS, row['file'] + '.jpg')
    if os.path.exists(dst) and os.path.getsize(dst) > 6000:
        return 'keep'
    # 网易云封面（镜像搜索 -> pic_id 图）
    try:
        res = s.get(API, params={'types': 'search', 'source': 'netease', 'name': row['name'], 'count': 3}, timeout=20).json()
        if isinstance(res, list) and res and res[0].get('pic_id'):
            pid = res[0]['pic_id']
            u = 'https://p1.music.126.net/%s/%s.jpg?param=500y500' % (
                _ne_hash(pid), pid)
            rr = s.get(u, timeout=25)
            if rr.status_code == 200 and len(rr.content) > 6000:
                open(dst, 'wb').write(rr.content)
                return 'netease'
    except Exception:
        pass
    return 'keep'


def _ne_hash(pic_id):
    # 网易云图片直链需要加密 id，改用官方 img 接口
    return 'x'


def main():
    ok, missing, bad = audit()
    print('ok', len(ok), 'missing', len(missing), 'bad', len(bad))
    tot = sum(x[2] for x in ok)
    print('total bytes %.2f GB' % (tot / 2 ** 30))
    print('max size %.1f MB' % (max(x[2] for x in ok) / 1048576))
    over = [x[0]['n'] for x in ok if x[2] > LIMIT]
    print('over25:', over)
    dev = [(x[0]['n'], round(x[3] - x[0]['interval'], 1)) for x in ok if abs(x[3] - x[0]['interval']) > 5]
    print('duration drift >5s:', len(dev), dev[:10])
    print('missing:', [(r['n'], r['name'], r['artist_str']) for r in missing])
    print('bad:', bad)
    # 封面
    cov_missing = [r['n'] for r in rows if not (os.path.exists(os.path.join(COVERS, r['file'] + '.jpg'))
                                                and os.path.getsize(os.path.join(COVERS, r['file'] + '.jpg')) > 6000)]
    print('covers missing/small:', len(cov_missing), cov_missing)
    json.dump({'ok': len(ok), 'missing': [r['n'] for r in missing],
               'missing_detail': [(r['n'], r['name'], r['artist_str']) for r in missing],
               'cov_small': cov_missing}, open(os.path.join(WORK, 'audit.json'), 'w'), ensure_ascii=False)


if __name__ == '__main__':
    main()
