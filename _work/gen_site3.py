# -*- coding: utf-8 -*-
"""生成 data/tracks.js 与 下载清单.csv（已剔除缺源曲目）。"""
import json, os, re, csv
import mutagen

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
SITE = os.path.join(BASE, '114514Songs')
FILES = os.path.join(SITE, 'SongsFiles')
COVERS = os.path.join(SITE, 'SongsCover')
DATA_DIR = os.path.join(SITE, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 最后一批人工修正
FIX = {613: '欧美电音', 614: '欧美电音', 606: '欧美电音', 607: '欧美电音', 529: '欧美电音',
       733: '欧美电音', 627: '欧美电音', 725: '欧美电音', 728: '欧美电音', 729: '欧美电音',
       232: 'vocaloid', 594: '其他', 593: '其他', 402: '其他'}

rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
cats = json.load(open(os.path.join(WORK, 'cats.json'), encoding='utf-8'))
for k, v in FIX.items():
    if str(k) in cats:
        cats[str(k)] = v
json.dump(cats, open(os.path.join(WORK, 'cats.json'), 'w'), ensure_ascii=False, indent=0)

tracks = []
for r in sorted(rows, key=lambda x: x['n']):
    n = r['n']
    exts = [e for e in ('.mp3', '.flac', '.m4a') if os.path.exists(os.path.join(FILES, r['file'] + e))]
    if not exts:
        continue
    ext = exts[0]
    p = os.path.join(FILES, r['file'] + ext)
    try:
        info = mutagen.File(p).info
        dur = round(float(info.length))
        br = int(getattr(info, 'bitrate', 0) or 0)
    except Exception:
        dur, br = r['interval'], 0
    q = 'FLAC' if ext == '.flac' else ('320k' if br >= 300000 else '128k')
    tracks.append({
        'n': n, 'title': r['name'], 'artist': r['artist_str'], 'album': r['album'],
        'cat': cats.get(str(n), '其他'), 'file': r['file'], 'ext': ext,
        'dur': dur, 'kb': round(os.path.getsize(p) / 1024), 'q': q,
        'cover': os.path.exists(os.path.join(COVERS, r['file'] + '.jpg')),
    })

meta = {
    'title': '114514123',
    'subtitle': 'QQ音乐歌单 · 本地音频漫游',
    'source': 'https://c6.y.qq.com/base/fcgi-bin/u?__=NLuTQkyqsfl4',
    'count': len(tracks),
    'seconds': sum(t['dur'] for t in tracks),
    'kb': sum(t['kb'] for t in tracks),
}

js = "/* 由 _work/gen_site3.py 生成；增删曲目请直接改 tracks 数组 */\nwindow.PLAYLIST = " + \
     json.dumps({'meta': meta, 'tracks': tracks}, ensure_ascii=False, indent=1) + ";\n"
open(os.path.join(DATA_DIR, 'tracks.js'), 'w', encoding='utf-8').write(js)

# CSV 清单
order = ['音游曲', 'vocaloid', '日语动漫/流行曲', '东方Project', '欧美电音', '纯音乐', '其他']
with open(os.path.join(SITE, '下载清单.csv'), 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.writer(f)
    w.writerow(['编号', '歌曲名', '歌手', '专辑', '分类', '文件名', '大小(MB)', '时长(秒)', '音质'])
    for i, t in enumerate(tracks, 1):
        w.writerow([i, t['title'], t['artist'], t['album'], t['cat'], t['file'] + t['ext'],
                    round(t['kb'] / 1024, 2), t['dur'], t['q']])

from collections import Counter
c = Counter(t['cat'] for t in tracks)
print('tracks', len(tracks))
for k in order:
    print(' ', k, c.get(k, 0))
print('sum GB %.2f' % (meta['kb'] / 1048576))
print('data file', os.path.getsize(os.path.join(DATA_DIR, 'tracks.js')) // 1024, 'KB')
