# -*- coding: utf-8 -*-
"""最后一轮：标题级宽松搜索（netease/joox），时长窗口 ±25s。"""
import json, os, re, time, threading, difflib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
API = 'https://music-api.gdstudio.xyz/api.php'
LIMIT = 25 * 1024 * 1024
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
STATUS = os.path.join(WORK, 'dl_status.json')
status = json.load(open(STATUS)) if os.path.exists(STATUS) else {}
lock = threading.Lock()
local = threading.local()
_last = [0.0]


def sess():
    s = getattr(local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        local.s = s
    return s


def api(params, tries=5):
    for i in range(tries):
        with lock:
            dt = time.time() - _last[0]
            if dt < 1.1:
                time.sleep(1.1 - dt)
            _last[0] = time.time()
        try:
            r = sess().get(API, params=params, timeout=25)
            if r.status_code == 200 and r.text.strip()[:1] in '[{':
                return r.json()
        except Exception:
            pass
        time.sleep(1.5 * (i + 1))
    return None


def norm(s):
    s = re.sub(r'[\(\)\[\]（）【】]', ' ', s or '')
    s = re.sub(r'[\s\-_,.、·:：!！?？\'"`~～&/+]', '', s)
    return s.lower()


def valid(path, row):
    if not os.path.exists(path) or os.path.getsize(path) < 300000 or os.path.getsize(path) > LIMIT:
        return False
    try:
        import mutagen
        f = mutagen.File(path)
        dur = float(f.info.length) if f and f.info else 0
    except Exception:
        return False
    return dur >= 30 and row['interval'] and abs(dur - row['interval']) <= 25


def fetch(url, dst):
    try:
        with sess().get(url, stream=True, timeout=90) as r:
            if r.status_code != 200:
                return False
            tmp = dst + '.part'
            n = 0
            with open(tmp, 'wb') as f:
                for c in r.iter_content(262144):
                    f.write(c)
                    n += len(c)
                    if n > LIMIT:
                        f.close(); os.remove(tmp); return False
            os.replace(tmp, dst)
            return True
    except Exception:
        return False


def tag(path, row):
    try:
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC, ID3NoHeaderError
        if os.path.splitext(path)[1].lower() != '.mp3':
            return
        cov = os.path.join(COVERS, row['file'] + '.jpg')
        data = open(cov, 'rb').read() if os.path.exists(cov) else None
        try:
            t = ID3(path)
        except ID3NoHeaderError:
            t = ID3()
        for k in ('TIT2', 'TPE1', 'TALB', 'TRCK', 'APIC'):
            t.delall(k)
        t.add(TIT2(encoding=3, text=row['name']))
        t.add(TPE1(encoding=3, text=row['artist_str']))
        t.add(TALB(encoding=3, text=row['album']))
        t.add(TRCK(encoding=3, text=str(row['n'])))
        if data:
            t.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=data))
        t.save(path, v2_version=3)
    except Exception:
        pass


def handle(row):
    n = row['n']
    dst = os.path.join(FILES, row['file'] + '.mp3')
    if valid(dst, row):
        return n, 'skip'
    tgt = norm(row['name'])
    for src in ('netease', 'joox'):
        songs = api({'types': 'search', 'source': src, 'name': row['name'], 'count': 10})
        if not isinstance(songs, list):
            continue
        songs = [c for c in songs if difflib.SequenceMatcher(None, tgt, norm(c.get('name') or '')).ratio() >= 0.5]
        songs.sort(key=lambda c: -difflib.SequenceMatcher(None, tgt, norm(c.get('name') or '')).ratio())
        for c in songs[:4]:
            info = api({'types': 'url', 'source': src, 'id': c['id'], 'br': 320})
            if not isinstance(info, dict) or not info.get('url'):
                continue
            if fetch(info['url'], dst) and valid(dst, row):
                tag(dst, row)
                return n, 'ok:%s-loose' % src
            if os.path.exists(dst):
                os.remove(dst)
    return n, 'miss'


def main():
    todo = [r for r in rows if not any(valid(os.path.join(FILES, r['file'] + e), r) for e in ('.mp3', '.flac', '.m4a'))]
    print('todo', len(todo), flush=True)
    res = {}
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(handle, r): r for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            r = futs[fut]
            try:
                n, out = fut.result()
            except Exception as e:
                n, out = r['n'], 'crash:%s' % e
            res[n] = out
            with lock:
                status[str(n)] = {'ok': out.startswith('ok'), 'result': out, 'file': r['file']}
            print(i, n, row_name(r), out, flush=True)
    with lock:
        snap = dict(status)
    json.dump(snap, open(STATUS + '.tmp', 'w'), ensure_ascii=False)
    os.replace(STATUS + '.tmp', STATUS)
    print('ok', sum(1 for v in status.values() if v.get('ok')), '/', len(rows))
    print('miss', sorted(n for n, v in res.items() if not v.startswith('ok')))


def row_name(r):
    return r['name'][:24]


if __name__ == '__main__':
    main()
