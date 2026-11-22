# -*- coding: utf-8 -*-
"""给 778 首已下载曲目分类：音游曲 / vocaloid / 日语动漫流行 / 东方Project / 欧美电音 / 纯音乐 / 其他。"""
import json, os, re

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

VOCALOID_SYNTH = [
    '初音ミク', '初音未来', '镜音铃', '镜音连', '鏡音', '巡音流歌', '巡音ルカ', 'KAITO', 'MEIKO', 'GUMI', 'グミ',
    'IA', '可不', 'KAFU', '重音テト', 'かさねてと', 'v flower', 'flower', '歌愛ユキ', '歌爱雪', '足立レイ',
    '音街ウナ', '音街鳗', 'ずんだもん', '洛天依', '赤羽', '星尘', '心华', '楽正綾', '結月ゆかり', '東北ずん子',
    'ONE', '春歌ナナ', '鳴花', 'ボカロ', 'VOCALOID', 'NEEDY GIRL OVERDOSE', '超てんちゃん',
]
VOCALOID_P = [
    'ピノキオピー', '匹诺曹P', 'かいりきベア', 'DECO*27', 'DECO27', 'デコ・ニーナ', '稲葉曇', 'inabakumori',
    'ナユタン星人', '柊マグネタイト', 'jon-YAKITORY', 'いよわ', 'なきそ', '40mP', 'wowaka', '現実逃避P',
    'ツミキ', 'はるまきごはん', '春卷饭', 'MIMI', 'ゆこぴ', 'Sohbana', 'マサラダ', '香椎モイミ', '内緒のピアス',
    '東京真中', 'kyiku', 'カササギ', '中村さんそ', '吉田夜世', 'SLAVE.V-V-R', 'うたたP', 'kemu', 'Neru',
    'halyosy', 'EasyPop', 'ryo', 'supercell', 'とあ', '椎名もた', 'MARETU', 'シャノン', 'ナナツカゼ',
    '暴飲暴食P', 'ぴーなた', 'picco', '水野あつ', 'shizuku', 'もちうつね', 'Mayonazy', 'はろける',
    '廃原メモリ', 'ルシノ', '真島ゆろ', '柿崎ユウタ', 'Atena', 'keeno', 'はるな。', 'サツキ', 'じん',
    '一二三', '傘村トータ', 'ナナホシ管弦楽団', 'かいりきベア', 'cosMo', '黒うさP', 'ゆうゆ', 'ユリイ・カノン',
    'とくみくす', 'Omoi', 'Orangestar', '蜜柑星P', 'Teniwoha', 'てにをは', 'かめりあ', 'kemu',
]
TOUHOU = [
    '東方', '幻想郷', 'フランドール', 'ナイト・オブ・ナイツ', 'Bad Apple', '上海アリス', '上海爱莉丝',
    '黄昏フロンティア', 'ビートまりお', 'COOL&CREATE', '森羅万象', 'あきやまうに', 'ZUN', 'マツヨイナイトバグ',
    '超最終鬼畜妹', '千年幻想郷', 'フラワリングナイト', '東方project', 'touhou', 'Touhou',
]
RHYTHM = [
    'USAO', 't+pazolite', 'REDALiCE', '打打だいず', 'かねこちはる', 'TJ.hangneil', 'パソコン音楽クラブ',
    'SEGA Sound Team', 'sasakure.UK', 'かめりあ', 'Camellia', '削除', 'Feryquitous', 'RoughSketch',
    'DJ Noriken', 'lapix', 'ARForest', 'Kobaryo', 'DJ Myosuke', 'Massive New Krew', 'Ryu☆', 'kors k',
    'Hommarju', 'P*Light', 'DJ Genki', 'BlackY', 'yooh', 'syatten', 'nora2r', 'm1dy', 'DJ' , 'A-One',
    'かめりあ', 'DJ TOTTO', 'RoughSketch', 't+pazolite', 'USAO', 'Sota Fujimori', 'NAOKI',
]
RHYTHM_ALBUM = ['maimai', 'CHUNITHM', 'チュウニズム', 'Arcaea', 'プロセカ', 'プロジェクトセカイ', 'オンゲキ',
                'beatmania', 'WACCA', 'GROOVE COASTER', 'Deemo', 'Cytus', 'Muse Dash', '音ゲー', 'SOUND VOLTEX', 'jubeat']
JPOP = [
    'YOASOBI', 'ヨアソビ', 'ヨルシカ', 'Yorushika', '米津玄師', 'LiSA', '织部里沙', 'Aimer', '宇多田',
    'RADWIMPS', '當山みれい', '当山真玲', '幾田りら', 'ikura', '花澤香菜', 'はなざわ', '鹿乃', '鎖那', 'さな',
    'yama', 'imase', 'あたらよ', 'Atarayo', 'こはならむ', 'Kohana Lam', 'ロクデナシ', 'Sou', 'Kotoha', 'ユイカ',
    'さんひ', 'tayori', 'Lia', '松原みき', 'Goose house', 'fripSide', '凛として時雨', '凛冽时雨',
    'トゲナシトゲアリ', 'TOGENASHI', 'HIMEHINA', '星街すいせい', 'まふまふ', 'mafumafu', '椎名もた',
    'RADWIMPS', 'Daoko', 'ダヲコ', '内緒のピアス', 'ナナツカゼ', 'Ren', 'yama', 'Ado', 'milet', '三無Marblue',
]
EDM = [
    'Vicetone', 'Alan Walker', 'ILLENIUM', 'Marshmello', 'The Chainsmokers', 'Kygo', 'Zedd', 'Martin Garrix',
    'David Guetta', 'R3HAB', 'SABAI', 'Feint', 'Tobu', 'Elektronomia', 'K-391', 'Tungevaag', 'Raaban',
    'Mike Perry', 'Gryffin', 'Said The Sky', 'Crystal Skies', 'Au5', 'Pegboard Nerds', 'Virtual Riot',
    'Dion Timmer', 'KSHMR', 'Alesso', 'Calvin Harris', 'Robin Schulz', 'Clean Bandit', 'Major Lazer',
    'DJ Snake', 'Steve Aoki', 'Kordhell', 'Dxrk', 'Hoang', 'Nevve', 'Dropgun', 'Chester Young', 'Feenixpawl',
    'Steerner', 'Martell', 'Raven & Kreyn', 'Wild Cards', 'VINAI', 'Far Out', 'Kastra', 'Curbi', 'RetroVision',
    'Timmy Trumpet', 'Carnage', 'Sevenn', 'Danny Avila', 'Tungevaag', 'LIONE', 'Kerli', 'Nurko', 'Dabin',
    'Said The Sky', 'Last Heroes', 'Jason Ross', 'Seven Lions', 'MitiS', 'William Black', 'Crystal Skies',
    'ARMNHMR', 'Yetep', 'Fairlane', 'Trivecta', 'Wooli', 'Sullivan King', 'Kai Wachi', 'PhaseOne',
    'Slushii', 'Panda Eyes', 'Teminite', 'Barely Alive', 'Discordance', 'Eliminate', 'Boombox Cartel',
    'Slander', 'NGHTMRE', 'Flux Pavilion', 'Zomboy', 'Excision', 'Skrillex', 'Diplo', 'A-Trak', 'Malaa',
    'Tchami', 'Mercer', 'Habstrakt', 'Ephwurd', 'Dombresky', 'Noizu', 'Chris Lake', 'Fisher', 'Dom Dolla',
    'John Summit', 'Meduza', 'ARTBAT', 'Camelphat', 'Solardo', 'Eli Brown', 'Charlotte de Witte',
    'Amelie Lens', 'Nina Kraviz', 'Boris Brejcha', 'Tale Of Us', 'Anyma', 'Adriatique', 'Innellea',
    'Bicep', 'Overmono', 'Fred again', 'Mura Masa', 'Disclosure', 'Duke Dumont', 'Gorgon City',
    'MK', 'Sonny Fodera', 'Low Steppa', 'Ferreck Dawn', 'Riton', 'Sigala', 'Jax Jones', 'Mabel',
    'Rudimental', 'Wilkinson', 'Sub Focus', 'Dimension', 'Culture Shock', 'Camo & Krooked', 'Mefjus',
    'Noisia', 'Ivy Lab', 'Alix Perez', 'Halogenix', 'Break', 'Total Science', 'dBridge', 'Calibre',
]
INSTRUMENTAL = [
    'C418', 'DJ OKAWARI', 'Pianoboy', '高至豪', '徐梦圆', 'Toby Fox', 'Laura Shigihara', 'Peter Roe',
    'Lightscape', 'Shirfine', 'Cymophane', 'Snigellin', 'MoreanP', 'm-taku', 'Kevin MacLeod', 'Bobby Cole',
    'John Dreamer', 'Two Steps From Hell', 'Thomas Bergersen', 'Steven Price', 'Hans Zimmer', 'Leandro Aconcha',
    '西郷憲一郎', 'Yuzuru箏', 'Eddie', 'Shin Giwon Piano', 'Eric Fullerton', 'Brad Knauber',
]
CN = ['洛天依']  # 中文虚拟歌手归 vocaloid

CATS = ['音游曲', 'vocaloid', '日语动漫/流行曲', '东方Project', '欧美电音', '纯音乐', '其他']


def hit(text, keys):
    t = text.lower()
    for k in keys:
        if k.lower() in t:
            return k
    return None


def classify(r):
    title = r['name']
    arts = r['artists']
    blob = title + ' ' + ' '.join(arts) + ' ' + (r.get('album') or '')

    if hit(blob, TOUHOU):
        return '东方Project'
    if hit(blob, VOCALOID_SYNTH) or hit(blob, VOCALOID_P):
        return 'vocaloid'
    if hit(blob, RHYTHM_ALBUM) or hit(' '.join(arts), RHYTHM):
        return '音游曲'
    if hit(' '.join(arts), JPOP):
        return '日语动漫/流行曲'
    if hit(' '.join(arts), EDM):
        return '欧美电音'
    if hit(' '.join(arts), INSTRUMENTAL):
        return '纯音乐'
    if re.search(r'\((Inst\.|inst\.|伴奏|纯音乐|Instrumental)', title):
        return '纯音乐'
    return '其他'


out = {}
for r in sel:
    out[str(r['n'])] = classify(r)

from collections import Counter
c = Counter(out.values())
print(dict(c), 'total', len(out))
json.dump(out, open(os.path.join(WORK, 'cats.json'), 'w'), ensure_ascii=False, indent=0)

print('\n=== 其他 (%d) ===' % c['其他'])
for r in sel:
    if out[str(r['n'])] == '其他':
        print(r['n'], r['name'][:40], '|', r['artist_str'][:46])
