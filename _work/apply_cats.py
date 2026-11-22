# -*- coding: utf-8 -*-
"""最终分类修正：把余下曲目按人工判断归位。"""
import json, os, re
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
cats = json.load(open(os.path.join(WORK, 'cats.json'), encoding='utf-8'))
rows = {r['n']: r for r in json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))}

EXTRA_EDM = [
    'disc0v3ry', 'hwaastyle', 'fregibot', 'dyrox', 'layzzz', 'aurora sky', 'org3', 'адлин', 'taylor swift',
    'dj hans', 'ginjo', 'southernlion南狮电音', 'dj zeng', 'nina nesbitt', 'di young', 'emma wahlin',
    'rémy', 'rosé', 'bruno mars', 'reynard silva', 'fly project', 'cotton eye joe', 'rednex',
    'maroon 5', 'alexandra stan', 'onerepublic', 'agera', 'anthony keyrouz', 'tezatalks', 'mrwhite',
    'alex guesta', 'kar play', 'imagine dragons', 'alex skrindo', 'lipps inc.', 'the fold', 'bebe rexha',
    'xufeih', 'mars', 'taiga', 'xxxtentacion', 'maxtaylor', 'rentz', 'professor green', 'adam christopher',
    'burgess', 'jessia', 'rich edwards', 'alec benjamin', 'hedley', 'spada', 'herobrine\'s life',
    'em beihold', 'michael henry montgomery', 'fall out boy', 'robin gan', 'the xx', 'halsey', 'crazy frog',
    'charlie puth', 'selena gomez', 'nightcall', 'malou', 'hillsong young & free', 'phoebe ryan',
    'one direction', 'carly rae jepsen', 'owl city', 'caviare', '2someone', 'powfu', 'beabadoobee',
    'project 46', 'olivia', 'alvaro soler', 'lenka', 'the kid laroi', 'justin bieber', '5 seconds of summer',
    'rachel platten', 'dj korea pop', 'shawn mendes', 'gavin degraw', 'jack stauber', 'dj hai cena',
    'max oazo', 'moonessa', 'imagine dragons', 'gamper & dadoni', 'akon', 'camila cabello', 'elyotto',
    'zedivan', 't-pain', 'ne-yo', 'pixie paris', 'mr. polska', 'maxriven', 'asher monroe', 'matilda',
    'chave', 'danny olson', 't.z', 'zella day', 'sub urban', 'black coast', 'm. maggie', 'sia', 'kina',
    'adriana proenza', 'dj blyatman', 'russian village boys', 'lady gaga', 'broiler', 'matisyahu',
    'alessia cara', 'linkin park', 'hawk nelson', 'jonathan steingard', 'cash cash', 'sofia reyes',
    'zayn', 'y2k', 'bbno$', 'darin', 'p!nk', 'thimlife', 'bibiane z', 'jonas blue', 'raye', 'dirty palm',
    'conor ross', 'chandler blasé', 'ember island', 'matte', 'tru concept', 'frogmonster', 'aaronicstuff',
    'christina perri', 'miani', 'tez cadey', 'rick astley', 'savior', 'adieu', 'voodoo', 'mellen gi',
    'tommee profitt', 'soulodku', 'dj kantik', 'lis', 'asher', 'matte', 'slushii', 'mediks', 'panda eyes',
    'dj okawari', 'daishi dance', 'cinnamons', 'evening cinema', 'zoe', 'murphy', 'palpit', 'kastra',
    'caviare', 'serings', 'icon audio', 'empty old city', 'vodke', 'hshk', 'ananya nabila', 'krewella',
    'shapov', 'cal', 'zoë', 'thefatrat', 'frogmonster', 'y2k', 'bbno$',
]
EXTRA_JPOP = ['yunomi', 'nicamoq', 'ゆのみ', 'にかもきゅ', 'michita', 'ミチタ', 'hanser', '瑞葵', 'mizuki',
              'daishi dance', 'cinnamons', 'evening cinema', 'empty old city', 'mikayla', 'akie秋绘']
EXTRA_INST = ['lindsey stirling', 'xue_tao_lu', '20001s1', 'yuzuru箏', 'allenvave', 'serings', 'icon audio']
EXTRA_V = ['r-906', 'ikayaki', 'ぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬぬ',
           'imagesdawn', 'ココアシガレットp', '初月', 'ゆーり', 'yuri']

# 逐曲指定（优先级最高）
OVR = {
    190: '欧美电音', 224: '欧美电音', 330: '其他', 400: '其他', 439: '其他', 495: '其他', 498: '其他',
    777: '其他', 293: '其他', 704: '其他',
    465: '纯音乐', 757: '纯音乐', 682: '纯音乐',
    12: 'vocaloid', 176: 'vocaloid', 192: 'vocaloid', 198: 'vocaloid', 209: 'vocaloid', 255: 'vocaloid',
    173: '日语动漫/流行曲', 194: '日语动漫/流行曲', 217: '日语动漫/流行曲', 590: '日语动漫/流行曲',
    749: '日语动漫/流行曲', 751: '日语动漫/流行曲', 710: '日语动漫/流行曲', 711: '日语动漫/流行曲',
    195: '欧美电音', 196: '欧美电音',
    782: '其他', 12: 'vocaloid',
}


def variants(a):
    s = a.strip().lower()
    out = {s}
    m = re.match(r'^(.*?)\s*[\(（]\s*(.*?)\s*[\)）]\s*$', s)
    if m:
        out.add(m.group(1).strip())
        out.add(m.group(2).strip())
    return out


def has(r, names):
    bag = set(names)
    for a in r['artists']:
        if variants(a) & bag:
            return True
    return False


for n_str, c in list(cats.items()):
    n = int(n_str)
    r = rows[n]
    if n in OVR:
        cats[n_str] = OVR[n]
        continue
    if c != '其他':
        continue
    if has(r, EXTRA_V):
        cats[n_str] = 'vocaloid'
    elif has(r, EXTRA_INST):
        cats[n_str] = '纯音乐'
    elif has(r, EXTRA_JPOP):
        cats[n_str] = '日语动漫/流行曲'
    elif has(r, EXTRA_EDM):
        cats[n_str] = '欧美电音'

json.dump(cats, open(os.path.join(WORK, 'cats.json'), 'w'), ensure_ascii=False, indent=0)
c = Counter(cats.values())
print(dict(c), 'total', len(cats))
rest = sorted(int(n) for n, v in cats.items() if v == '其他')
print('其他', len(rest))
for n in rest:
    print('%d|%s|%s' % (n, rows[n]['name'][:36], rows[n]['artist_str'][:28]))
