# -*- coding: utf-8 -*-
"""稳健版补漏下载器：网易云(320k/128k) -> QQ音乐游客(128k)。严格校验，原子写状态。"""
import json, os, re, time, threading, difflib, hashlib
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
CACHE = {}


def sess():
    s = getattr(local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update({'User-Agent': UA})
        local.s = s
    return s


def norm(s):
    s = re.sub(r'[\(\)\[\]（）【】]', ' ', s or '')
    s = re.sub(r'[\s\-_,.、·:：!！?？\'"`~～&/+]', '', s)
    return s.lower()


def valid(path, row):
    if not os.path.exists(path):
        return False, 0
    sz = os.path.getsize(path)
    if sz < 400000 or sz > LIMIT:
        return False, sz
    try:
        import mutagen
        f = mutagen.File(path)
        if not f or not f.info:
            return False, sz
        dur = float(f.info.length)
    except Exception:
        return False, sz
    if not dur or dur < 30:
        return False, sz
    if row['interval'] and abs(dur - row['interval']) > 15:
        return False, sz
    return True, sz


def fetch_stream(url, dst, referer='https://music.163.com/'):
    try:
        with sess().get(url, stream=True, timeout=90, headers={'Referer': referer}) as r:
            if r.status_code != 200:
                return False
            tmp = dst + '.part'
            n = 0
            with open(tmp, 'wb') as f:
                for c in r.iter_content(262144):
                    f.write(c)
                    n += len(c)
                    if n > LIMIT:
                        f.close()
                        os.remove(tmp)
                        return False
            os.replace(tmp, dst)
            return True
    except Exception:
        return False


def ne_search(row):
    key = str(row['n'])
    with lock:
        if key in CACHE:
            return CACHE[key]
    q = '%s %s' % (row['name'], row['artists'][0] if row['artists'] else '')
    songs = []
    for i in range(3):
        try:
            r = sess().get('https://music.163.com/api/search/get',
                           params={'s': q, 'type': 1, 'limit': 10, 'offset': 0},
                           headers={'Referer': 'https://music.163.com/'}, timeout=20)
            songs = (r.json().get('result') or {}).get('songs') or []
            break
        except Exception:
            time.sleep(1 + i)
    with lock:
        CACHE[key] = songs
    return songs


def pick(songs, row):
    tgt = norm(row['name'])
    arts = set(norm(a) for a in row['artists'])
    best, sc0 = None, 0
    for c in songs:
        n = norm(c['name'])
        sim = difflib.SequenceMatcher(None, tgt, n).ratio()
        if sim < 0.62:
            continue
        car = set(norm(a['name']) for a in c.get('artists', []))
        sc = sim + (0.8 if n == tgt else 0) + (1.2 if arts & car else 0)
        if sc > sc0:
            best, sc0 = c, sc
    return best


def ne_urls(song_id):
    try:
        r = sess().get('https://music.163.com/api/song/enhance/player/url/v1',
                       params={'ids': json.dumps([song_id]), 'level': 'exhigh', 'encodeType': 'mp3'},
                       headers={'Referer': 'https://music.163.com/'}, timeout=20)
        d = (r.json().get('data') or [{}])[0]
        if d.get('code') == 200 and d.get('url'):
            yield d['url'], int(d.get('br') or 0)
    except Exception:
        pass
    yield 'https://music.163.com/song/media/outer/url?id=%s.mp3' % song_id, 128000


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


def qq_guest_url(row):
    mid = row['mid']
    s = sess()
    p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
        "guid": "10000", "songmid": [mid], "songtype": [0],
        "filename": ['M500%s%s.mp3' % (mid, mid)],
        "uin": "0", "loginflag": 1, "platform": "20"}},
        "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0}}
    try:
        d = s.post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20,
                   headers={'Referer': 'https://y.qq.com/'}).json()['req_0']['data']
        m = d['midurlinfo'][0]
        if m.get('purl'):
            sip = [x for x in d.get('sip', []) if x]
            return (sip[0] if sip else 'https://ws.stream.qqmusic.qq.com/') + m['purl']
    except Exception:
        pass
    return None


def handle(row):
    n = row['n']
    dst = os.path.join(FILES, row['file'] + '.mp3')
    ok, _ = valid(dst, row)
    if ok:
        return n, 'skip'

    songs = ne_search(row)
    best = pick(songs, row) if songs else None
    if best:
        for url, br in ne_urls(best['id']):
            if fetch_stream(url, dst):
                ok, _ = valid(dst, row)
                if ok:
                    tag(dst, row)
                    return n, 'ok:netease-%d' % (320 if br >= 320000 else 128)
                os.path.exists(dst) and os.remove(dst)

    u = qq_guest_url(row)
    if u:
        if fetch_stream(u, dst, 'https://y.qq.com/'):
            ok, _ = valid(dst, row)
            if ok:
                tag(dst, row)
                return n, 'ok:qq-128'
            os.path.exists(dst) and os.remove(dst)
    return n, 'miss'


def save_status():
    tmp = STATUS + '.tmp'
    with lock:
        snap = {k: v for k, v in status.items()}
    json.dump(snap, open(tmp, 'w'), ensure_ascii=False)
    os.replace(tmp, STATUS)


def main():
    todo = []
    for r in rows:
        exts = ['.mp3', '.flac', '.m4a']
        if any(valid(os.path.join(FILES, r['file'] + e), r)[0] for e in exts):
            status[str(r['n'])] = {'ok': True, 'result': 'existing', 'file': r['file']}
            continue
        todo.append(r)
    print('todo', len(todo), flush=True)
    done = 0
    results = {}
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(handle, r): r for r in todo}
        for fut in as_completed(futs):
            r = futs[fut]
            try:
                n, res = fut.result()
            except Exception as e:
                n, res = r['n'], 'crash:%s' % e
            done += 1
            results[n] = res
            with lock:
                status[str(n)] = {'ok': res.startswith('ok'), 'result': res, 'file': r['file']}
            if done % 10 == 0:
                save_status()
                print('progress %d/%d' % (done, len(todo)), flush=True)
    save_status()
    ok = sum(1 for v in status.values() if v.get('ok'))
    print('OK total', ok, '/', len(rows), flush=True)
    print('miss', sorted(n for n, r in results.items() if not r.startswith('ok')), flush=True)


if __name__ == '__main__':
    main()
