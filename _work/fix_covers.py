# -*- coding: utf-8 -*-
"""补全缺失封面：QQ 详情 -> 网易云专辑图 -> 占位图。"""
import json, os, sys, requests
from io import BytesIO

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
s = requests.Session()
s.headers.update({'User-Agent': UA, 'Referer': 'https://y.qq.com/'})


def qq_album(mid):
    try:
        p = {"req_0": {"module": "music.pf_song_detail_svr", "method": "get_song_detail",
                       "param": {"song_mid": mid}},
             "comm": {"uin": "0", "format": "json", "ct": 24, "cv": 0}}
        d = s.post('https://u.y.qq.com/cgi-bin/musicu.fcg', json=p, timeout=20).json()
        return (d['req_0']['data']['track_info']['album'].get('mid') or '').strip()
    except Exception:
        return ''


def ne_cover(row):
    try:
        r = s.get('https://music.163.com/api/search/get',
                  params={'s': row['name'], 'type': 1, 'limit': 5, 'offset': 0},
                  headers={'Referer': 'https://music.163.com/'}, timeout=20)
        songs = (r.json().get('result') or {}).get('songs') or []
        if songs:
            return songs[0].get('album', {}).get('picUrl') or ''
    except Exception:
        pass
    return ''


def save(url, dst):
    try:
        r = s.get(url, timeout=25)
        if r.status_code == 200 and len(r.content) > 2048:
            open(dst, 'wb').write(r.content)
            return True
    except Exception:
        pass
    return False


def placeholder(dst, text):
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (500, 500), (32, 32, 32))
        d = ImageDraw.Draw(img)
        font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 34)
        # 自动换行
        ctx, line, lines = '', '', []
        for ch in text:
            if d.textlength(ctx + ch, font=font) > 430:
                lines.append(ctx)
                ctx = ''
            ctx += ch
        lines.append(ctx)
        y = 250 - len(lines) * 22
        for ln in lines[:6]:
            w = d.textlength(ln, font=font)
            d.text(((500 - w) / 2, y), ln, font=font, fill=(200, 200, 200))
            y += 46
        img.save(dst, 'JPEG', quality=90)
        return True
    except Exception:
        return False


def main():
    fixed = {'qq': 0, 'netease': 0, 'ph': 0, 'fail': []}
    for row in rows:
        dst = os.path.join(COVERS, row['file'] + '.jpg')
        if os.path.exists(dst) and os.path.getsize(dst) > 2048:
            continue
        mid = row['albummid'] or qq_album(row['mid'])
        if mid and save('https://y.gtimg.cn/music/photo_new/T002R500x500M000%s.jpg' % mid, dst):
            fixed['qq'] += 1
            continue
        pic = ne_cover(row)
        if pic and save(pic + '?param=500y500', dst):
            fixed['netease'] += 1
            continue
        if placeholder(dst, row['name']):
            fixed['ph'] += 1
            continue
        fixed['fail'].append(row['n'])
    print(fixed)


if __name__ == '__main__':
    main()
