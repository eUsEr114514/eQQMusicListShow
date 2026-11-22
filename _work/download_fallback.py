# -*- coding: utf-8 -*-
"""备用源下载：网易云（优先 320k）-> QQ音乐游客 128k。写入标签与封面，严格 <=25MB。"""
import json, os, re, time, threading, difflib
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
LIMIT = 25 * 1024 * 1024
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
STATUS = os.path.join(WORK, 'dl_status.json')
status = json.load(open(STATUS)) if os.path.exists(STATUS) else {}
lock = threading.Lock()
local = threading.local()
ne_cache_path = os.path.join(WORK, 'netease_cache.json')
ne_cache = json.load(open(ne_cache_path)) if os.path.exists(ne_cache_path) else {}


def sess():
    s = getattr(local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        local.s = s
    return s


def norm(s):
    s = re.sub(r'[\(\)\[\]（）【】]', ' ', s or '')
    s = re.sub(r'[\s\-_,.、·:：!！?？\'"`~～&/]+', '', s)
    return s.lower()


def ne_search(row):
    key = str(row['n'])
    if key in ne_cache:
        return ne_cache[key]
    q = '%s %s' % (row['name'], row['artists'][0] if row['artists'] else '')
    out = []
    for attempt in range(3):
        try:
            r = sess().get('https://music.163.com/api/search/get',
                           params={'s': q, 'type': 1, 'limit': 12, 'offset': 0},
                           headers={'Referer': 'https://music.163.com/'}, timeout=20)
            j = r.json()
            out = (j.get('result') or {}).get('songs') or []
            break
        except Exception:
            time.sleep(1 + attempt)
    ne_cache[key] = out
    return out


def pick(cands, row):
    tgt = norm(row['name'])
    arts = set(norm(a) for a in row['artists'])
    best, score = None, 0
    for c in cands:
        n = norm(c['name'])
        sim = difflib.SequenceMatcher(None, tgt, n).ratio()
        car = set(norm(a['name']) for a in c.get('artists', []))
        overlap = len(arts & car) > 0
        dur_ok = abs((c.get('duration') or 0) / 1000.0 - row['interval']) < 20
        sc = sim * (2 if n == tgt else 1) + (1.5 if overlap else 0) + (0.5 if dur_ok else 0)
        if sim < 0.55:
            continue
        if sc > score:
            best, score = c, sc
    return best


def ne_url(song_id):
    try:
        r = sess().get('https://music.163.com/api/song/enhance/player/url/v1',
                       params={'ids': json.dumps([song_id]), 'level': 'exhigh', 'encodeType': 'mp3'},
                       headers={'Referer': 'https://music.163.com/'}, timeout=20)
        d = (r.json().get('data') or [{}])[0]
        if d.get('code') == 200 and d.get('url'):
            return d['url'], d.get('br', 0)
    except Exception:
        pass
    try:
        r = sess().get('https://music.163.com/song/media/outer/url?id=%s.mp3' % song_id,
                       headers={'Referer': 'https://music.163.com/'}, timeout=20, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 100000:
            return ('MEM', song_id), 0
    except Exception:
        pass
    return None, 0


def qq_guest(row):
    mid = row['mid']
    fns = ['M500%s%s.mp3' % (mid, mid)]
    s = sess()
    s.headers.pop('Cookie', None)
    p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
        "guid": "10000", "songmid": [mid], "songtype": [0], "filename": fns,
        "uin": "0", "loginflag": 1, "platform": "20"}},
        "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0}}
    try:
        d = s.post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20).json()['req_0']['data']
        m = d['midurlinfo'][0]
        if m.get('purl'):
            sip = [x for x in d.get('sip', []) if x]
            return (sip[0] if sip else 'https://ws.stream.qqmusic.qq.com/') + m['purl']
    except Exception:
        pass
    return None


def fetch(url, dst):
    try:
        if isinstance(url, tuple):
            data = sess().get('https://music.163.com/song/media/outer/url?id=%s.mp3' % url[1],
                              headers={'Referer': 'https://music.163.com/'}, timeout=60).content
            if len(data) < 100000:
                return False
            open(dst, 'wb').write(data)
            return True
        with sess().get(url, stream=True, timeout=60) as r:
            if r.status_code != 200:
                return False
            total = 0
            tmp = dst + '.part'
            with open(tmp, 'wb') as f:
                for chunk in r.iter_content(262144):
                    f.write(chunk)
                    total += len(chunk)
                    if total > LIMIT:
                        f.close()
                        os.remove(tmp)
                        return False
            os.replace(tmp, dst)
            return True
    except Exception:
        return False


def duration(path):
    try:
        import mutagen
        f = mutagen.File(path)
        return float(f.info.length) if f and f.info else 0.0
    except Exception:
        return 0.0


def tag(path, row):
    try:
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC, ID3NoHeaderError
        ext = os.path.splitext(path)[1].lower()
        cov = os.path.join(COVERS, row['file'] + '.jpg')
        covdata = open(cov, 'rb').read() if os.path.exists(cov) else None
        if ext == '.mp3':
            try:
                tags = ID3(path)
            except ID3NoHeaderError:
                tags = ID3()
            for k in ('TIT2', 'TPE1', 'TALB', 'TRCK', 'APIC'):
                tags.delall(k)
            tags.add(TIT2(encoding=3, text=row['name']))
            tags.add(TPE1(encoding=3, text=row['artist_str']))
            tags.add(TALB(encoding=3, text=row['album']))
            tags.add(TRCK(encoding=3, text=str(row['n'])))
            if covdata:
                tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=covdata))
            tags.save(path, v2_version=3)
    except Exception:
        pass


def handle(row):
    n = row['n']
    if status.get(str(n), {}).get('ok'):
        return n, 'skip'
    cands = ne_search(row)
    best = pick(cands, row) if cands else None
    if best:
        url, br = ne_url(best['id'])
        if url:
            dst = os.path.join(FILES, row['file'] + '.mp3')
            if fetch(url, dst):
                ln = duration(dst)
                if ln and row['interval'] and abs(ln - row['interval']) > 15:
                    os.remove(dst)
                else:
                    tag(dst, row)
                    return n, 'ok:netease-%s' % ('320' if br >= 320000 else '128')
    u = qq_guest(row)
    if u:
        dst = os.path.join(FILES, row['file'] + '.mp3')
        if fetch(u, dst):
            ln = duration(dst)
            if not ln or not row['interval'] or abs(ln - row['interval']) <= 15:
                tag(dst, row)
                return n, 'ok:qq-guest'
            os.remove(dst)
    return n, 'miss'


def main():
    todo = [r for r in rows if not status.get(str(r['n']), {}).get('ok')]
    print('todo', len(todo), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(handle, r): r for r in todo}
        for fut in as_completed(futs):
            r = futs[fut]
            try:
                n, res = fut.result()
            except Exception as e:
                n, res = r['n'], 'crash:%s' % e
            done += 1
            with lock:
                status[str(n)] = {'ok': res.startswith('ok'), 'result': res, 'file': r['file']}
                if done % 20 == 0:
                    json.dump(status, open(STATUS, 'w'), ensure_ascii=False)
                    json.dump(ne_cache, open(ne_cache_path, 'w'), ensure_ascii=False)
                    print('progress %d/%d' % (done, len(todo)), flush=True)
    json.dump(status, open(STATUS, 'w'), ensure_ascii=False)
    json.dump(ne_cache, open(ne_cache_path, 'w'), ensure_ascii=False)
    ok = sum(1 for v in status.values() if v.get('ok'))
    print('DONE ok', ok, '/', len(rows), flush=True)
    print('missing', sorted(int(k) for k, v in status.items() if not v.get('ok')), flush=True)


if __name__ == '__main__':
    main()
