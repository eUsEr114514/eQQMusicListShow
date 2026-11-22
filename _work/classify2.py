# -*- coding: utf-8 -*-
"""第二版分类：艺人与标题映射 + 逐曲兜底覆盖。"""
import json, os, re
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
have = set()
for f in os.listdir(FILES):
    m = re.match(r'^(\d+)-', f)
    if m:
        have.add(int(m.group(1)))
sel = [r for r in rows if r['n'] in have]

# 艺人（子串匹配，按顺序优先）
ART = [
    # ---- 东方Project ----
    ('东方Project', ['东方', 'touhou', 'ZUN', '上海アリス', '上海爱莉丝', 'ビートまりお', 'COOL&CREATE', '森羅万象',
                     'あきやまうに', '黄昏フロンティア', 'Cathy', 'fi-fy', 'まろん', '千年幻想郷', 'フランドール']),
    # ---- vocaloid ----
    ('vocaloid', ['初音', 'ミク', '镜音', '鏡音', '巡音', 'KAITO', 'MEIKO', 'GUMI', 'グミ', 'IA (', '可不', 'KAFU',
                  '重音テト', 'かさねてと', 'flower', '歌愛ユキ', '歌爱雪', '足立レイ', '音街', 'ずんだもん',
                  '洛天依', '赤羽', '星尘', '心华', '楽正綾', '結月ゆかり', '東北ずん子', 'ボカロ', 'VOCALOID',
                  'ピノキオピー', '匹诺曹', 'かいりきベア', 'DECO', '稲葉曇', 'inabakumori', 'ナユタン星人',
                  '柊マグネタイト', 'jon-YAKITORY', 'いよわ', 'なきそ', '40mP', 'wowaka', '現実逃避P', 'ツミキ',
                  'はるまきごはん', '春卷饭', 'MIMI', 'ゆこぴ', 'Sohbana', 'マサラダ', '香椎モイミ', '内緒のピアス',
                  '東京真中', 'kyiku', 'カササギ', '中村さんそ', '吉田夜世', 'SLAVE.V-V-R', 'うたたP', 'kemu', 'Neru',
                  'halyosy', 'EasyPop', 'ryo', 'supercell', 'とあ', '椎名もた', 'MARETU', 'シャノン', 'ナナツカゼ',
                  '暴飲暴食P', 'ぴーなた', 'picco', '水野あつ', 'shizuku', 'もちうつね', 'Mayonazy', 'はろける',
                  '廃原メモリ', 'ルシノ', '真島ゆろ', '柿崎ユウタ', 'Atena', 'keeno', 'はるな。', 'サツキ', 'じん',
                  'cosMo', '黒うさP', 'ゆうゆ', 'ユリイ・カノン', 'てにをは', 'Orangestar', '蜜柑星P', 'wotaku',
                  'SHIKI', 'Magens', 'ヤバス', 'りぃふ', 'タカオカミズキ', 'TRAP CHICK', 'SEVENTHLINKS', 'えいぷ',
                  'Chinozo', 'ilem', '乌龟Sui', '忘川风华录', 'anamanaguchi', 'TAK (', 'Kankitsu', 'otone',
                  'テヅカ', '3L (', 'Ponchi♪', 'はぁち', 'NANIMONO', '超てんちゃん', '原口沙輔', '横田商会',
                  'HIMEHINA', 'sunny', 'ツユ', 'TUYU']),
    # ---- 音游曲 ----
    ('音游曲', ['USAO', 't+pazolite', 'REDALiCE', '打打だいず', 'かねこちはる', 'TJ.hangneil', 'パソコン音楽クラブ',
                'Pasocom Music Club', 'SEGA Sound Team', 'sasakure.UK', 'かめりあ', 'Camellia', '削除', 'Feryquitous',
                'RoughSketch', 'Kobaryo', 'lapix', 'ARForest', 'DJ Noriken', 'DJ Myosuke', 'BlackY', 'yooh',
                'syatten', 'Kankitsu', 'Cosmograph', 'Rintaro Soma', 'otone', 'テヅカ', 'owl*tree', 'Benza', 'Zekk',
                'PIKASONIC', 'Tatsunoshin', 'Sota Fujimori', 'Ryu☆', 'kors k', 'Hommarju', 'P*Light', 'DJ TOTTO',
                'Massive New Krew', 'nora2r', 'm1dy', 'DJ Genki', 'A-One', 'カモメサノエレクトリック',
                'kamome sano', '月島春果', 'Neona', 'Tatsunoshin', 'Arctic', 'EmoCosine', 'Silentroom',
                'Feryquitous', 'かめりあ', 'アリスシャッハと魔法の楽団', 'Junction', 'HyuN', 'Nhato', 'Taishi',
                'かめりあ', 'DJ Noriken']),
    # ---- 日语动漫/流行曲 ----
    ('日语动漫/流行曲', ['YOASOBI', 'ヨアソビ', 'ヨルシカ', 'Yorushika', '米津玄師', 'LiSA', '织部里沙', 'Aimer',
                          '宇多田', 'RADWIMPS', '當山みれい', '当山真玲', '幾田りら', 'ikura', '花澤香菜', 'はなざわ',
                          '鹿乃', '鎖那', 'さな', 'yama', 'imase', 'あたらよ', 'Atarayo', 'こはならむ', 'Kohana Lam',
                          'ロクデナシ', 'Sou', 'Kotoha', 'ユイカ', 'さんひ', 'tayori', 'Lia', '松原みき', 'Goose house',
                          'fripSide', '凛として時雨', '凛冽时雨', 'トゲナシトゲアリ', 'TOGENASHI', '星街すいせい',
                          'まふまふ', 'mafumafu', 'SawanoHiroyuki', '澤野弘之', 'sakanaction', 'サカナクション',
                          'こっちのけんと', '吉本おじさん', 'ワンダーランズ', 'KOTOKO', 'NEEDY GIRL OVERDOSE',
                          'ツユ', 'TUYU', 'Akie秋绘', 'Daoko', 'ダヲコ', '花たん', '雨衣', '月乃', 'ナナツカゼ',
                          'HIMEHINA', 'Ponchi♪', 'Mikayla', 'Rey', 'あたらよ']),
    # ---- 欧美电音 ----
    ('欧美电音', ['Vicetone', 'Alan Walker', 'ILLENIUM', 'Marshmello', 'Chainsmokers', 'Kygo', 'Zedd', 'Martin Garrix',
                 'David Guetta', 'R3HAB', 'SABAI', 'Feint', 'Tobu', 'Elektronomia', 'K-391', 'Tungevaag', 'Raaban',
                 'Mike Perry', 'Gryffin', 'Said The Sky', 'Crystal Skies', 'Au5', 'Pegboard Nerds', 'Virtual Riot',
                 'Dion Timmer', 'KSHMR', 'Alesso', 'Calvin Harris', 'Robin Schulz', 'Clean Bandit', 'Major Lazer',
                 'DJ Snake', 'Steve Aoki', 'Kordhell', 'Dxrk', 'Hoang', 'Nevve', 'Dropgun', 'Chester Young',
                 'Feenixpawl', 'Steerner', 'Martell', 'Raven & Kreyn', 'Wild Cards', 'VINAI', 'Far Out', 'Kastra',
                 'Timmy Trumpet', 'Carnage', 'Sevenn', 'Danny Avila', 'LIONE', 'Avicii', 'Dash Berlin', 'Krewella',
                 'King CAAN', 'ELYSA', 'BEAUZ', 'JVNA', 'Culture Code', 'Manse', 'Mediks', 'Nora En Pure',
                 'Matisse', 'Danko', 'Tyron Hapi', 'J Lisk', 'Elephante', 'Deep Chills', 'Cartoon', 'Futuristik',
                 'Robin Hustin', 'Janji', 'Cedric Gervais', 'Skan', 'Disco Fries', 'Besomorph', '3LAU', 'Tim Legend',
                 'Varien', 'Interupt', 'F.O.O.L', 'Pixel Terror', 'pluko', 'Egzod', 'Madnap', 'Ahxello', 'Arc North',
                 'New Beat Order', 'Aseks', 'Damien N-Drix', 'CHROMANCE', 'Approaching Nirvana', 'Valence', 'Monogem',
                 'Rival', 'Cadmium', 'Harley Bird', 'Remady', 'Manu-L', 'Zerky', 'AZNE', 'Katie Sky', 'Aaron Smith',
                 'Tanir & Tyomcha', 'Luma', 'Karra', 'Daya', 'Lennon Stella', 'Shy Martin', 'MKJ', 'Teminite',
                 'Jake Miller', 'JVLA', 'Russ', 'MAX', 'Chromeo', 'Fifth Harmony', 'Mae Stephens', 'George Ezra',
                 'Troye Sivan', 'Ava Max', 'Jaymes Young', 'Bishu', 'Blanke', 'Midnight Kids', 'Mark Sixma',
                 'Shapov', 'Palpit', 'Murphy', 'Hi Noise', 'Neon Tribe', 'Morris 5', 'Bvrnout', 'Britt Lari',
                 'Katelyn Tarver', 'UNSECRET', 'Terror Jr', 'Just Kiddin', 'Behmer', 'BEAUZ', 'Manse', 'Matteo',
                 'LeeAlive', 'Paul Wallen', 'Gigi Nally', 'Maggie Lindemann', 'Cheat Codes', 'CADE', 'pluko',
                 'pronouncedyea', 'JIDA', 'Leat\'eq', 'Pixel Terror', 'XYPO', 'M. Fischer', 'Acreix', 'Gelato',
                 'Hella', 'Pusher', 'Mothica', 'Shawn Wasabi', 'Tim Legend', 'Transviolet', '3LAU', 'Besomorph',
                 'Dendix', 'Agus Santoso', 'Robin Hustin', 'TobiMorrow', 'Jex', 'Skan', 'Krale', 'LBLVNC',
                 'Cedric Gervais', 'Digital Farm Animals', 'Dallas Austin', 'Santorini', 'Janji', 'DeeJay Ghost',
                 'Cartoon', 'Futuristik', 'Mikk Mäe', 'Emelie', 'Danko', 'Lulleaux', 'Kid Princess', 'Marmalade',
                 'Jacob Tillberg', 'DEAF KEV', 'Rameses B', 'Anna Yvette', 'NOTD', 'FADI', 'Wild', 'EH!DE', 'Tule',
                 'Chris Linton', 'Mr FijiWiji', 'AgNO3', 'Laura Brehm', 'SeVen.13', 'Krista Marina', 'Else', 'graves',
                 'Tim Gunter', 'LocateEmilio', 'Night Remix', 'Lucky Luke', 'Shane 54', 'Cubicore', 'Eric Lumiere',
                 'Matluck', 'Reinn', 'Mark Sixma', 'Regi', 'Jake Reese', 'Shapov', 'Palpit', 'Mes', 'Tuno',
                 'Bvrnout', 'AXYL', 'Ray Le Fanue', 'Culture Code', 'Karra', 'Katelyn Tarver', 'Novaspace', 'Vade',
                 'TYSM', 'Lazer Boomerang', 'Suprafive', 'Nora En Pure', 'Mediks', 'Cyan Lpegd', 'TheReal FatBoi',
                 'New Beat Order', 'Aaron Richards', 'Jonasu', 'LeeAlive', 'Fdby', 'Matteo', 'Matisse & Sadko',
                 'Hanne Mjøen', 'Ahxello', 'Ash (', 'Madnap', 'Pauline Herr', 'Dave Rodgers', 'sapientdream',
                 'Maggie Lindemann', 'Cheat Codes', 'pluko', 'Egzod', 'JIDA', 'Rachel Lim', 'Leat\'eq', 'Pixel Terror',
                 'Emeline', 'XYPO', 'Acreix', 'Gelato', 'Hella', 'Pusher', 'Mothica', 'Transviolet', 'Interupt',
                 'Luna LePage', 'Ms-TearGas', 'Ku', 'Hikoor']),
    # ---- 纯音乐 ----
    ('纯音乐', ['C418', 'DJ OKAWARI', 'Pianoboy', '高至豪', '徐梦圆', 'Toby Fox', 'Laura Shigihara', 'Peter Roe',
                'Lightscape', 'Shirfine', 'Cymophane', 'Snigellin', 'MoreanP', 'm-taku', 'Kevin MacLeod',
                'Bobby Cole', 'John Dreamer', 'Two Steps From Hell', 'Thomas Bergersen', 'Steven Price',
                'Leandro Aconcha', '西郷憲一郎', 'Yuzuru箏', 'Shin Giwon Piano', 'Eric Fullerton', 'Brad Knauber',
                'Jay Vincent', 'Michael Kramer', 'Gameloft', 'Krubb Wenkroist', 'Icon Audio', 'Eddie']),
]
# 明确的兜底覆盖（歌曲序号 -> 分类）
OVR = {}


def match(text, keys):
    t = text.lower()
    for k in keys:
        if k.lower() in t:
            return True
    return False


def classify(r):
    n = r['n']
    if n in OVR:
        return OVR[n]
    blob = (r['name'] + ' ' + ' '.join(r['artists']) + ' ' + (r.get('album') or ''))
    arts = ' '.join(r['artists'])
    for cat, keys in ART:
        if match(blob, keys):
            return cat
    if re.search(r'\((Inst\.|inst\.|伴奏|Instrumental)', r['name']):
        return '纯音乐'
    return '其他'


if __name__ == '__main__':
    out = {str(r['n']): classify(r) for r in sel}
    c = Counter(out.values())
    print(dict(c), 'total', len(out))
    json.dump(out, open(os.path.join(WORK, 'cats.json'), 'w'), ensure_ascii=False, indent=0)
    print('\n=== 其他 (%d) ===' % c['其他'])
    for r in sorted(sel, key=lambda x: x['n']):
        if out[str(r['n'])] == '其他':
            print('%d|%s|%s' % (r['n'], r['name'][:42], r['artist_str'][:36]))
