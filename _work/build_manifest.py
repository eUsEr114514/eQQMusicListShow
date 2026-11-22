# -*- coding: utf-8 -*-
import json, re

sl = json.load(open('DownloadSongs/_work/playlist_raw.json', encoding='utf-8'))['cdlist'][0]['songlist']

# 声库/P主缺失补全表：序号 -> 需要补上的另一位
EXTRA = {
    1: "初音ミク", 19: "初音ミク", 23: "初音ミク", 28: "初音ミク", 43: "初音ミク", 45: "初音ミク",
    47: "初音ミク", 59: "初音ミク", 60: "初音ミク", 85: "初音ミク", 89: "初音ミク", 95: "初音ミク",
    98: "初音ミク", 105: "初音ミク", 106: "初音ミク", 107: "初音ミク", 118: "初音ミク", 122: "初音ミク",
    133: "初音ミク", 139: "重音テト", 143: "可不", 144: "初音ミク", 148: "初音ミク", 149: "歌愛ユキ",
    151: "初音ミク", 152: "初音ミク", 161: "初音ミク", 162: "歌愛ユキ", 172: "初音ミク", 174: "初音ミク",
    175: "可不", 193: "初音ミク", 199: "初音ミク", 201: "歌愛ユキ", 225: "初音ミク",
    62: "ユリイ・カノン", 96: "乌龟Sui", 163: "ゆうゆ", 764: "黒うさP",
}

BS = chr(92)


def sanitize(name):
    name = name.replace('/', '／').replace(BS, '＼').replace('|', '｜')
    name = re.sub(r'[<>:"?*\x00-\x1f]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip().rstrip('. ')
    if len(name) > 110:
        name = name[:110].rstrip('. ')
    return name


rows = []
used = {}
for n, s in enumerate(sl, 1):
    arts = [x.get('name', '').strip() for x in s.get('singer', []) if x.get('name')]
    if n in EXTRA and EXTRA[n] not in arts:
        arts = arts + [EXTRA[n]]
    base = sanitize(s['songname'].strip())
    fname = "%d-%s" % (n, base)
    if fname.lower() in used:
        used[fname.lower()] += 1
        fname = "%s (%d)" % (fname, used[fname.lower()])
    else:
        used[fname.lower()] = 1
    rows.append({
        'n': n, 'name': s['songname'].strip(), 'file': fname,
        'artists': arts, 'artist_str': ' / '.join(arts),
        'album': s.get('albumname', '').strip(), 'albummid': s.get('albummid', ''),
        'mid': s['songmid'], 'interval': int(s.get('interval') or 0),
        'size320': int(s.get('size320') or 0), 'size128': int(s.get('size128') or 0),
        'sizeflac': int(s.get('sizeflac') or 0),
    })

json.dump(rows, open('DownloadSongs/_work/manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('songs', len(rows))
print('sample:', rows[0]['file'], '|', rows[0]['artist_str'])
print('longest file len:', max(len(r['file']) for r in rows))
print('renamed dups:', sum(1 for r in rows if '(2)' in r['file']))
