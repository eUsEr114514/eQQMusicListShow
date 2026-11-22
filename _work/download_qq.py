# -*- coding: utf-8 -*-
"""按歌单顺序下载完整音频（FLAC 优先，其次 320k/128k MP3），严格 <=25MB，写入标签与封面。"""
import json, os, sys, threading, time, random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
os.makedirs(FILES, exist_ok=True)

LIMIT = 25 * 1024 * 1024
cookies = {c['name']: c['value'] for c in json.load(open(os.path.join(WORK, 'cookies.json'))) if 'qq.com' in c['domain']}
UIN = cookies.get('uin', '')
JAR = 'uin=%s; qm_keyst=%s; qqmusic_key=%s' % (UIN, cookies.get('qm_keyst', ''), cookies.get('qqmusic_key', ''))
HEAD = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
    'Referer': 'https://y.qq.com/', 'Cookie': JAR,
}
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
avail = json.load(open(os.path.join(WORK, 'avail_vip.json')))
STATUS_PATH = os.path.join(WORK, 'dl_status.json')
status = json.load(open(STATUS_PATH)) if os.path.exists(STATUS_PATH) else {}
lock = threading.Lock()
local = threading.local()

TIERS = [
    ('flac', 'F000', '.flac', 'sizeflac'),
    ('mp3_320', 'M800', '.mp3', 'size320'),
    ('mp3_128', 'M500', '.mp3', 'size128'),
    ('m4a_128', 'C400', '.m4a', None),
]


def sess():
    s = getattr(local, 's', None)
    if s is None:
        s = requests.Session()
        s.headers.update(HEAD)
        local.s = s
    return s


def vkey_for(mid):
    fns, tiers = [], []
    for t, pre, ext, _ in TIERS:
        fns.append('%s%s%s%s' % (pre, mid, mid, ext))
        tiers.append(t)
    p = {"req_0": {"module": "vkey.GetVkeyServer", "method": "CgiGetVkey", "param": {
        "guid": "10000", "songmid": [mid] * len(fns), "songtype": [0] * len(fns), "filename": fns,
        "uin": UIN, "loginflag": 1, "platform": "20"}},
        "comm": {"uin": UIN, "format": "json", "ct": 24, "cv": 0}}
    d = sess().post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=25).json()
    data = d['req_0']['data']
    sips = [x for x in data.get('sip', []) if x]
    out = {}
    for i, m in enumerate(data.get('midurlinfo', [])):
        if i < len(tiers) and m.get('purl'):
            out[tiers[i]] = m['purl']
    return out, sips


def download(url, dst):
    with sess().get(url, stream=True, timeout=60) as r:
        if r.status_code != 200:
            return False, 'http %d' % r.status_code
        total = 0
        tmp = dst + '.part'
        with open(tmp, 'wb') as f:
            for chunk in r.iter_content(256 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                total += len(chunk)
                if total > LIMIT:
                    f.close()
                    os.remove(tmp)
                    return False, 'over25mb'
        os.replace(tmp, dst)
        return True, total


def probe_len(path):
    try:
        import mutagen
        f = mutagen.File(path)
        return float(f.info.length) if f and f.info else 0.0
    except Exception:
        return 0.0


def tag(path, row):
    try:
        import mutagen
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC, ID3NoHeaderError
        from mutagen.mp4 import MP4Cover
        ext = os.path.splitext(path)[1].lower()
        cov = os.path.join(COVERS, row['file'] + '.jpg')
        covdata = open(cov, 'rb').read() if os.path.exists(cov) else None
        if ext == '.flac':
            from mutagen.flac import FLAC, Picture
            f = FLAC(path)
            f['title'] = row['name']
            f['artist'] = row['artist_str']
            f['album'] = row['album']
            f['tracknumber'] = str(row['n'])
            if covdata:
                pic = Picture()
                pic.type = 3
                pic.mime = 'image/jpeg'
                pic.data = covdata
                f.clear_pictures()
                f.add_picture(pic)
            f.save()
        elif ext == '.mp3':
            try:
                tags = ID3(path)
            except ID3NoHeaderError:
                tags = ID3()
            tags.delall('TIT2'); tags.delall('TPE1'); tags.delall('TALB'); tags.delall('TRCK'); tags.delall('APIC')
            tags.add(TIT2(encoding=3, text=row['name']))
            tags.add(TPE1(encoding=3, text=row['artist_str']))
            tags.add(TALB(encoding=3, text=row['album']))
            tags.add(TRCK(encoding=3, text=str(row['n'])))
            if covdata:
                tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=covdata))
            tags.save(path, v2_version=3)
        elif ext == '.m4a':
            from mutagen.mp4 import MP4
            f = MP4(path)
            f['\xa9nam'] = [row['name']]
            f['\xa9ART'] = [row['artist_str']]
            f['\xa9alb'] = [row['album']]
            f['trkn'] = [(row['n'], 0)]
            if covdata:
                f['covr'] = [MP4Cover(covdata, imageformat=MP4Cover.FORMAT_JPEG)]
            f.save()
        return True
    except Exception as e:
        return 'tagfail:%s' % e


def handle(row):
    n = row['n']
    mid = row['mid']
    st = status.get(str(n), {})
    if st.get('ok'):
        return n, 'skip'
    q = avail.get(mid, {})
    order = []
    for t, pre, ext, sizekey in TIERS:
        if not q.get(t):
            continue
        if sizekey:
            sz = row.get(sizekey) or 0
            if sz and sz > LIMIT:
                continue
        order.append((t, pre, ext))
    if not order:
        return n, 'no-source'

    try:
        urls, sips = vkey_for(mid)
    except Exception as e:
        return n, 'vkey-err:%s' % e
    if not urls:
        return n, 'no-vkey'
    base = sips[0] if sips else 'https://ws.stream.qqmusic.qq.com/'

    for t, pre, ext in order:
        purl = urls.get(t)
        if not purl:
            continue
        dst = os.path.join(FILES, row['file'] + ext)
        ok = False
        for attempt in range(3):
            try:
                ok, info = download(base + purl, dst)
            except Exception as e:
                ok, info = False, 'exc:%s' % e
            if ok:
                break
            if isinstance(info, str) and info.startswith('http'):
                try:
                    urls, sips = vkey_for(mid)
                    base = sips[0] if sips else base
                    purl = urls.get(t) or purl
                except Exception:
                    pass
            time.sleep(1)
        if not ok:
            continue
        length = probe_len(dst)
        if row['interval'] and length and abs(length - row['interval']) > 12:
            os.remove(dst)
            continue
        tag(dst, row)
        return n, 'ok:%s:%.1fMB' % (t, os.path.getsize(dst) / 1048576)
    return n, 'all-tiers-failed'


def main():
    todo = [r for r in rows if not status.get(str(r['n']), {}).get('ok')]
    tn = os.environ.get('TEST_N')
    if tn:
        todo = todo[:int(tn)]
    print('todo', len(todo), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
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
                    json.dump(status, open(STATUS_PATH, 'w'), ensure_ascii=False)
                    print('progress %d/%d' % (done, len(todo)), flush=True)
    json.dump(status, open(STATUS_PATH, 'w'), ensure_ascii=False)
    ok = sum(1 for v in status.values() if v.get('ok'))
    print('DONE ok', ok, 'of', len(rows), flush=True)
    bad = [(int(k), v['result']) for k, v in status.items() if not v.get('ok')]
    print('bad', sorted(bad)[:80], flush=True)


if __name__ == '__main__':
    main()
