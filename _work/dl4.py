# -*- coding: utf-8 -*-
"""第四阶段：对剩余缺口做宽松匹配重试（netease -> joox -> QQ游客）。"""
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
GAP = 1.2


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
            if dt < GAP:
                time.sleep(GAP - dt)
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
    s = re.sub(r'(dj版|dj|伴奏|remix|cover|翻唱|完整版)', '', s, flags=re.I)
    return s.lower()


def valid(path, row):
    if not os.path.exists(path):
        return False
    sz = os.path.getsize(path)
    if sz < 300000 or sz > LIMIT:
        return False
    try:
        import mutagen
        f = mutagen.File(path)
        dur = float(f.info.length) if f and f.info else 0
    except Exception:
        return False
    if dur < 30:
        return False
    return row['interval'] and abs(dur - row['interval']) <= 20


def pick(songs, row, thr=0.5):
    tgt = norm(row['name'])
    arts = set(norm(a) for a in row['artists'])
    best, sc0 = None, 0
    for c in songs or []:
        n = norm(c['name'])
        sim = difflib.SequenceMatcher(None, tgt, n).ratio()
        if sim < thr:
            continue
        car = set(norm(a) for a in (c.get('artist') or []))
        sc = sim + (0.5 if n == tgt else 0) + (1.0 if arts & car else 0)
        if sc > sc0:
            best, sc0 = c, sc
    return best


def fetch(url, dst):
    try:
        with sess().get(url, stream=True, timeout=120) as r:
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


def qq_guest_url(row):
    mid = row['mid']
    p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
        "guid": "10000", "songmid": [mid], "songtype": [0],
        "filename": ['M500%s%s.mp3' % (mid, mid)], "uin": "0", "loginflag": 1, "platform": "20"}},
        "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0}}
    try:
        d = sess().post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20,
                        headers={'Referer': 'https://y.qq.com/'}).json()['req_0']['data']
        m = d['midurlinfo'][0]
        if m.get('purl'):
            sip = [x for x in d.get('sip', []) if x]
            return (sip[0] if sip else 'https://ws.stream.qqmusic.qq.com/') + m['purl']
    except Exception:
        pass
    return None


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


def try_source(row, src, keyword, thr=0.5):
    songs = api({'types': 'search', 'source': src, 'name': keyword, 'count': 10})
    best = pick(songs, row, thr) if isinstance(songs, list) else None
    if not best:
        return None
    info = api({'types': 'url', 'source': src, 'id': best['id'], 'br': 320})
    if not isinstance(info, dict) or not info.get('url'):
        return None
    dst = os.path.join(FILES, row['file'] + '.mp3')
    if fetch(info['url'], dst) and valid(dst, row):
        tag(dst, row)
        return 'ok:%s-%s' % (src, info.get('br') or '?')
    if os.path.exists(dst):
        os.remove(dst)
    return None


def handle(row):
    n = row['n']
    dst = os.path.join(FILES, row['file'] + '.mp3')
    if valid(dst, row):
        return n, 'skip'
    kws = ['%s %s' % (row['name'], row['artists'][0] if row['artists'] else ''), row['name']]
    for kw in kws:
        for src in ('netease', 'joox'):
            out = try_source(row, src, kw, 0.5 if kw == kws[0] else 0.42)
            if out:
                return n, out
    u = qq_guest_url(row)
    if u and fetch(u, dst) and valid(dst, row):
        tag(dst, row)
        return n, 'ok:qq-128'
    if os.path.exists(dst):
        os.remove(dst)
    return n, 'miss'


def save():
    with lock:
        snap = dict(status)
    json.dump(snap, open(STATUS + '.tmp', 'w'), ensure_ascii=False)
    os.replace(STATUS + '.tmp', STATUS)


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
            if i % 5 == 0:
                save()
                print('progress %d/%d' % (i, len(todo)), flush=True)
    save()
    print('ok', sum(1 for v in status.values() if v.get('ok')), '/', len(rows), flush=True)
    print('miss', sorted(n for n, v in res.items() if not v.startswith('ok')), flush=True)


if __name__ == '__main__':
    main()
