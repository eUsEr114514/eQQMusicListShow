# -*- coding: utf-8 -*-
"""下载 789 首歌的专辑封面到 SongsCover，命名与音频一致。"""
import json, os, sys, time
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, '114514Songs', 'SongsCover')
os.makedirs(OUT, exist_ok=True)

rows = json.load(open(os.path.join(BASE, '_work', 'manifest.json'), encoding='utf-8'))
HEAD = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
    'Referer': 'https://y.qq.com/',
}

session = requests.Session()
session.headers.update(HEAD)

cache = {}


def fetch(row):
    dst = os.path.join(OUT, row['file'] + '.jpg')
    if os.path.exists(dst) and os.path.getsize(dst) > 2048:
        return ('skip', row['n'])
    mid = row['albummid']
    if mid in cache:
        data = cache[mid]
    else:
        data = None
        for size in ('500x500', '300x300'):
            url = 'https://y.gtimg.cn/music/photo_new/T002R%sM000%s.jpg' % (size, mid)
            for _ in range(3):
                try:
                    r = session.get(url, timeout=20)
                    if r.status_code == 200 and len(r.content) > 2048 and r.content[:2] == b'\xff\xd8':
                        data = r.content
                        break
                except Exception:
                    time.sleep(1)
            if data:
                break
        cache[mid] = data
    if not data:
        return ('fail', row['n'])
    with open(dst, 'wb') as f:
        f.write(data)
    return ('ok', row['n'])


def main():
    stats = {'ok': 0, 'skip': 0, 'fail': 0}
    fails = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        for i, (st, n) in enumerate(ex.map(fetch, rows), 1):
            stats[st] += 1
            if st == 'fail':
                fails.append(n)
            if i % 100 == 0:
                print('progress %d/789 %s' % (i, stats), flush=True)
    print('DONE', stats, 'fails', fails, flush=True)


if __name__ == '__main__':
    main()
