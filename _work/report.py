# -*- coding: utf-8 -*-
"""生成交付报告：CSV 清单 + Markdown 汇总。"""
import json, os, csv
import mutagen

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))


def quality(p):
    try:
        f = mutagen.File(p)
        ext = os.path.splitext(p)[1].lower()
        if ext == '.flac':
            return 'FLAC'
        br = int(getattr(f.info, 'bitrate', 0) or 0)
        if br >= 300000:
            return 'MP3-320k'
        if br >= 200000:
            return 'MP3-VBR~256k'
        return 'MP3-128k'
    except Exception:
        return 'unknown'


def main():
    out = []
    missing = []
    for r in rows:
        cand = [e for e in ('.mp3', '.flac', '.m4a') if os.path.exists(os.path.join(FILES, r['file'] + e))]
        cov = os.path.join(COVERS, r['file'] + '.jpg')
        if not cand:
            missing.append(r)
            out.append([r['n'], r['name'], r['artist_str'], r['album'], '', '', '', '', '缺失'])
            continue
        p = os.path.join(FILES, r['file'] + cand[0])
        sz = os.path.getsize(p)
        try:
            dur = float(mutagen.File(p).info.length)
        except Exception:
            dur = 0
        out.append([r['n'], r['name'], r['artist_str'], r['album'],
                    os.path.basename(p), round(sz / 1048576, 2), round(dur, 1),
                    quality(p), '封面:' + ('有' if os.path.exists(cov) else '无')])

    csv_path = os.path.join(BASE, '114514Songs', '下载清单.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['序号', '歌曲名', '歌手', '专辑', '文件名', '大小(MB)', '时长(秒)', '音质', '封面'])
        w.writerows(out)

    from collections import Counter
    q = Counter(x[7] for x in out if x[7] != '缺失')
    total = sum(x[5] for x in out if x[5])
    print('csv', csv_path)
    print('quality', dict(q))
    print('total GB %.2f' % (total / 1024))
    print('missing', [(r['n'], r['name']) for r in missing])


if __name__ == '__main__':
    main()
