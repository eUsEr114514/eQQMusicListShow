# -*- coding: utf-8 -*-
"""第五阶段：用 QQ 搜索找同曲的其他版本/专辑，用游客 vkey 下载 128k 补洞。"""
import json, os, re, time, threading, difflib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
LIMIT = 25 * 1024 * 1024
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
STATUS = os.path.join(WORK, 'dl_status.json')
status = json.load(open(STATUS)) if os.path.exists(STATUS) else {}
lock = threading.Lock()
local = threading.local()


def sess():
    s = getattr(local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA, 'Referer': 'https://y.qq.com/'})
        local.s = s
    return s


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
    return dur >= 30 and row['interval'] and abs(dur - row['interval']) <= 15


def search(q):
    try:
        r = sess().get('https://c.y.qq.com/soso/fcgi-bin/client_search_cp',
                       params={'w': q, 'format': 'json', 'n': 12, 'p': 1, 'cr': 1, 'new_json': 1},
                       timeout=20)
        return ((r.json().get('data') or {}).get('song') or {}).get('list') or []
    except Exception:
        return []


def guest_url(mid):
    p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
        "guid": "10000", "songmid": [mid], "songtype": [0],
        "filename": ['M500%s%s.mp3' % (mid, mid)], "uin": "0", "loginflag": 1, "platform": "20"}},
        "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0}}
    try:
        d = sess().post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20).json()['req_0']['data']
        m = d['midurlinfo'][0]
        if m.get('purl'):
            sip = [x for x in d.get('sip', []) if x]
            return (sip[0] if sip else 'https://ws.stream.qqmusic.qq.com/') + m['purl']
    except Exception:
        pass
    return None


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
    singer = row['artists'][0] if row['artists'] else ''
    cands = search('%s %s' % (row['name'], singer))
    if not cands:
        cands = search(row['name'])
    cands.sort(key=lambda c: -difflib.SequenceMatcher(None, tgt, norm(c.get('name') or c.get('title') or '')).ratio())
    for c in cands[:8]:
        mid = c.get('mid') or c.get('songmid')
        nm = c.get('name') or c.get('title') or ''
        if not mid:
            continue
        if difflib.SequenceMatcher(None, tgt, norm(nm)).ratio() < 0.6:
            continue
        iv = c.get('interval') or 0
        if row['interval'] and iv and abs(iv - row['interval']) > 15:
            continue
        u = guest_url(mid)
        if u and fetch(u, dst) and valid(dst, row):
            tag(dst, row)
            return n, 'ok:qq-alt'
        if os.path.exists(dst):
            os.remove(dst)
    return n, 'miss'


def main():
    todo = [r for r in rows if not any(valid(os.path.join(FILES, r['file'] + e), r) for e in ('.mp3', '.flac', '.m4a'))]
    print('todo', len(todo), flush=True)
    res = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
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
            print(i, n, out, flush=True)
    json.dump(status, open(STATUS + '.tmp', 'w'), ensure_ascii=False)
    os.replace(STATUS + '.tmp', STATUS)
    print('ok', sum(1 for v in status.values() if v.get('ok')), '/', len(rows))
    print('miss', sorted(n for n, v in res.items() if not v.startswith('ok')))


if __name__ == '__main__':
    main()
