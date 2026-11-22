# -*- coding: utf-8 -*-
"""对最后 13 首逐个人工确认候选并下载（时长门限 ±20s）。"""
import json, os, time, sys
import requests, mutagen

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
API = 'https://music-api.gdstudio.xyz/api.php'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
rows = {r['n']: r for r in json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))}
s = requests.Session()
s.headers.update({'User-Agent': UA})

# 手工确认的候选：(序号, [netease id 列表按优先级])
CAND = {
    288: ['1451720450'],
    530: [],
    586: ['1824751735', '1835516913'],
    560: ['25694409'],
    780: ['1393834238', '1399135155'],
    782: ['1383023894'],
    788: ['531295576'],
    789: [],
    264: ['504265014'],
    744: [],
    776: [],
    517: [],
    329: ['442869301'],
}


def tag(path, row):
    try:
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, APIC, ID3NoHeaderError
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


def main():
    for n, ids in CAND.items():
        if not ids:
            print(n, 'no candidate')
            continue
        row = rows[n]
        dst = os.path.join(FILES, row['file'] + '.mp3')
        got = False
        for sid in ids:
            try:
                info = s.get(API, params={'types': 'url', 'source': 'netease', 'id': sid, 'br': 320}, timeout=25).json()
            except Exception as e:
                print(' ', sid, 'url err', str(e)[:40])
                time.sleep(2)
                continue
            u = info.get('url')
            if not u:
                print(' ', sid, 'no url')
                continue
            try:
                r = s.get(u, timeout=90)
                if r.status_code != 200 or len(r.content) < 300000:
                    continue
                open(dst, 'wb').write(r.content)
                dur = float(mutagen.File(dst).info.length)
                ok = abs(dur - row['interval']) <= 20
                print(n, sid, 'dur %.1f vs %d -> %s' % (dur, row['interval'], 'OK' if ok else 'reject'))
                if ok:
                    tag(dst, row)
                    st = json.load(open(os.path.join(WORK, 'dl_status.json')))
                    st[str(n)] = {'ok': True, 'result': 'ok:manual-%s' % sid, 'file': row['file']}
                    json.dump(st, open(os.path.join(WORK, 'dl_status.json'), 'w'), ensure_ascii=False)
                    got = True
                    break
                os.remove(dst)
            except Exception as e:
                print(' ', sid, 'dl err', str(e)[:50])
            time.sleep(1.5)
        print(n, 'filled' if got else 'still missing', flush=True)
        time.sleep(2)


if __name__ == '__main__':
    main()
