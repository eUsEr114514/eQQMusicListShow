# -*- coding: utf-8 -*-
"""第三版分类：精确艺人名匹配 + 标题关键词 + 人工覆盖。"""
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

VOCALOID = {
    # 声库
    '初音ミク', '初音未来', '镜音铃', '镜音连', '鏡音リン', '鏡音レン', '巡音流歌', '巡音ルカ', 'kaito', 'meiko',
    'gumi', 'グミ', 'ia', 'イア', '可不', 'kafu', '重音テト', 'かさねてと', 'v flower', 'flower', '歌愛ユキ',
    '歌爱雪', '足立レイ', '音街ウナ', '音街鳗', 'ずんだもん', '洛天依', '赤羽', '星尘', '心华', '楽正綾',
    '結月ゆかり', '東北ずん子', 'ボカロ', 'vocaloid',
    # P主 / 制作人
    'ピノキオピー', '匹诺曹p', 'かいりきベア', 'deco*27', 'deco27', 'デコ・ニーナ', '稲葉曇', 'inabakumori',
    'ナユタン星人', '柊マグネタイト', 'jon-yakitory', 'いよわ', 'なきそ', '40mp', 'wowaka', '現実逃避p',
    'ツミキ', 'はるまきごはん', '春卷饭', 'mimi', 'ゆこぴ', 'sohbana', 'マサラダ', '香椎モイミ', '内緒のピアス',
    '東京真中', 'kyiku', 'カササギ', '中村さんそ', '吉田夜世', 'slave.v-v-r', 'うたたp', 'kemu', 'neru',
    'halyosy', 'easypop', 'ryo', 'supercell', 'とあ', '椎名もた', 'maretu', 'シャノン', 'ナナツカゼ',
    '暴飲暴食p', 'ぴーなた', 'picco', '水野あつ', 'shizuku', 'もちうつね', 'mayonazy', 'はろける',
    '廃原メモリ', 'ルシノ', '真島ゆろ', '柿崎ユウタ', 'atena', 'keeno', 'はるな。', 'サツキ', 'cosmo',
    '黒うさp', 'ゆうゆ', 'ユリイ・カノン', 'てにをは', 'orangestar', '蜜柑星p', 'wotaku', 'shiki', 'magens',
    'ヤバス', 'タカオカミズキ', 'trap chick', 'seventhl Inks', 'seventhl Inks', 'えいぷ', 'chinozo', 'ilem',
    '乌龟sui', '忘川风华录', 'anamanaguchi', 'tak', 'pONCHI♪', 'ponchi♪', 'はぁち', 'nANIMONO', 'nanimono',
    '超てんちゃん', '原口沙輔', '横田商会', 'himehina', 'kankitsu', 'otone', 'テヅカ', '3l', 'ねこぼーろ',
    'tiara', 'maretu', '傘村トータ', '一二三', 'てにをは', 'かめりあ', 'kemu', 'shino', 'shizuku',
}
TOUHOU_ART = {
    'cool&create', 'ビートまりお', '森羅万象', 'hayamism', '上海アリス幻樂団', '上海爱莉丝幻乐团',
    '黄昏フロンティア', 'あきやまうに', 'cathy', 'fi-fy', 'まろん', 'zun',
}
TOUHOU_TITLE = ['幻想郷', 'フランドール', 'ナイト・オブ・ナイツ', 'bad apple', '千年幻想郷', 'フラワリングナイト',
                '超最終鬼畜妹', 'マツヨイナイトバグ', '三妖精', '東方project', '少女綺想曲', '亡き王女']
RHYTHM = {
    'usao', 't+pazolite', 'redalice', '打打だいず', 'かねこちはる', 'tj.hangneil', 'パソコン音楽クラブ',
    'pasocom music club', 'sega sound team', 'sasakure.uk', 'かめりあ', 'camellia', '削除', 'feryquitous',
    'roughsketch', 'kobaryo', 'lapix', 'arforest', 'dj noriken', 'dj myosuke', 'blacky', 'yooh', 'syatten',
    'cosmograph', 'rintaro soma', 'owl*tree', 'benza', 'zekk', 'pikasonic', 'tatsunoshin', 'sota fujimori',
    'ryu☆', 'kors k', 'hommarju', 'p*light', 'dj totto', 'massive new krew', 'nora2r', 'm1dy', 'dj genki',
    'a-one', 'カモメサノエレクトリックオーケストラ', 'kamome sano', '月島春果', 'neona', 'sasakure.UK',
    'hyun', 'nhato', 'taishi', 'yuta imai', 'icone', 'dj katsu', 'dj' ,
}
JPOP = {
    'yoasobi', 'ヨアソビ', 'ヨルシカ', 'yorushika', '米津玄師', 'lisa', '织部里沙', 'aimer', '宇多田ヒカル',
    '宇多田光', 'radwimps', '當山みれい', '当山真玲', '幾田りら', 'ikura', '花澤香菜', 'はなざわ かな', '鹿乃',
    '鎖那', 'さな', 'yama', 'imase', 'あたらよ', 'atarayo', 'こはならむ', 'kohana lam', 'ロクデナシ', 'sou',
    'kotoha', 'ユイカ', '『ユイカ』', 'さんひ', 'tayori', 'lia', '松原みき', 'goose house', 'fripside',
    'tk from 凛冽时雨', '凛冽时雨', 'トゲナシトゲアリ', 'togenashi togeari', '星街すいせい', 'まふまふ',
    'mafumafu', 'sawanohiroyuki[nzk]', '澤野弘之', '泽野弘之', 'sakanaction', 'サカナクション', 'こっちのけんと',
    '吉本おじさん', 'ワンダーランズ×ショウタイム', 'kotoko', 'needy girl overdose', 'ツユ', 'tuyu', 'akie秋绘',
    'daoko', 'ダヲコ', '雨衣', '月乃', 'ナナツカゼ', 'himehina', 'mikayla', 'rey', 'taku', 'テヅカ',
    '藍井エイル', 'fripSide', 'eir aoi', 'halca', 'sajou no hana', 'who-ya extended', 'yama',
}
EDM = {
    'vicetone', 'alan walker', 'illenium', 'marshmello', 'the chainsmokers', 'kygo', 'zedd', 'martin garrix',
    'david guetta', 'r3hab', 'sabai', 'feint', 'tobu', 'elektronomia', 'k-391', 'tungevaag', 'raaban',
    'mike perry', 'gryffin', 'said the sky', 'crystal skies', 'au5', 'pegboard nerds', 'virtual riot',
    'dion timmer', 'kshmr', 'alesso', 'calvin harris', 'robin schulz', 'clean bandit', 'major lazer',
    'dj snake', 'steve aoki', 'kordhell', 'dxrk ダーク', 'hoang', 'nevve', 'dropgun', 'chester young',
    'feenixpawl', 'steerner', 'martell', 'raven & kreyn', 'wild cards', 'vinai', 'far out', 'kastra',
    'timmy trumpet', 'carnage', 'sevenn', 'danny avila', 'lione', 'avicii', 'dash berlin', 'krewella',
    'king caan', 'elysa', 'beauz', 'jvna', 'culture code', 'manse', 'mediks', 'nora en pure', 'matisse & sadko',
    'danko', 'tyron hapi', 'j lisk', 'elephante', 'deep chills', 'cartoon', 'futuristik', 'robin hustin',
    'janji', 'cedric gervais', 'skan', 'disco fries', 'besomorph', '3lau', 'tim legend', 'varien', 'interupt',
    'f.o.o.l', 'pixel terror', 'pluko', 'egzod', 'madnap', 'ahxello', 'arc north', 'new beat order', 'aseks',
    'damien n-drix', 'chromance', 'approaching nirvana', 'valence', 'monogem', 'rival', 'cadmium', 'harley bird',
    'remady', 'manu-l', 'zerky', 'azne', 'katie sky', 'aaron smith', 'tanir & tyomcha', 'luma', 'karra',
    'daya', 'lennon stella', 'shy martin', 'mkj', 'teminite', 'jake miller', 'jvla', 'russ', 'max',
    'chromeo', 'fifth harmony', 'mae stephens', 'george ezra', 'troye sivan', 'ava max', 'jaymes young',
    'bishu', 'blanke', 'midnight kids', 'mark sixma', 'shapov', 'palpit', 'murphy', 'hi noise', 'neon tribe',
    'morris 5', 'bvrnout', 'britt lari', 'katelyn tarver', 'unsecret', 'terror jr', 'just kiddin', 'behmer',
    'matteo', 'leealive', 'paul wallen', 'gigi nally', 'maggie lindemann', 'cheat codes', 'cade', 'pronouncedyea',
    'jida', "leat'eq", 'xypo', 'm. fischer', 'acreix', 'gelato', 'hella', 'pusher', 'mothica', 'shawn wasabi',
    'transviolet', 'dendix', 'agus santoso', 'tobimorrow', 'jex', 'krale', 'lblvnc', 'digital farm animals',
    'dallas austin', 'santorini', 'deejay ghost', 'mikk mäe', 'emelie', 'lulleaux', 'kid princess', 'marmalade',
    'jacob tillberg', 'deaf kev', 'rameses b', 'anna yvette', 'notd', 'fadi', 'wild', 'eh!de', 'tule',
    'chris linton', 'mr fijiwiji', 'agno3', 'laura brehm', 'seven.13', 'krista marina', 'else', 'graves',
    'tim gunter', 'locateemilio', 'night remix', 'lucky luke', 'shane 54', 'cubicore', 'eric lumiere', 'matluck',
    'reinn', 'regi', 'jake reese', 'mes', 'tuno', 'axyl', 'ray le fanue', 'novaspace', 'vade', 'tysm',
    'lazer boomerang', 'suprafive', 'cyan lpegd', 'thereal fatboi', 'aaron richards', 'jonasu', 'fdby',
    'hanne mjøen', 'ash', 'madnap', 'pauline herr', 'dave rodgers', 'sapientdream', 'emeline', 'interupt',
    'luna lepage', 'ms-teargas', 'vØj', 'narvent', 'nueki', 'tolchonov', 'glichery', 'sma$her', 'murksh',
    'murkish', 'nightcore', 'strangerboi24', 'zayni', 'besomorph', 'robin hustin', 'marshmello',
    'kordhell', 'henry young', 'ashley alisha', 'jori king', 'ehrling', 'fredji', 'jubël', 'deepend',
}
INST = {
    'c418', 'dj okawari', 'pianoboy', 'pianoboy高至豪', '高至豪', '徐梦圆', 'toby fox', 'laura shigihara',
    'peter roe', 'lightscape', 'shirfine', 'cymophane', 'snigellin', 'moreanp', 'm-taku', 'kevin macleod',
    'bobby cole', 'john dreamer', 'two steps from hell', 'thomas bergersen', 'steven price', 'leandro aconcha',
    '西郷憲一郎', 'yuzuru箏', 'shin giwon piano', 'eric fullerton', 'brad knauber', 'jay vincent',
    'michael kramer', 'gameloft', 'krubb wenkroist', 'icon audio', 'eddie', 'serings', 'allenvave',
}
# 逐曲兜底（序号 -> 分类）
OVR = {
    76: 'vocaloid', 573: '其他',
}
TITLE_INST = re.compile(r'\((Inst\.|inst\.|伴奏|Instrumental|纯音乐|钢琴版)', re.I)


def variants(a):
    s = a.strip().lower()
    out = {s}
    m = re.match(r'^(.*?)\s*[\(（]\s*(.*?)\s*[\)）]\s*$', s)
    if m:
        out.add(m.group(1).strip())
        out.add(m.group(2).strip())
    return out


def artist_hit(r, bag):
    for a in r['artists']:
        if variants(a) & bag:
            return True
    return False


def classify(r):
    n = r['n']
    if n in OVR:
        return OVR[n]
    title_l = r['name'].lower()
    if artist_hit(r, TOUHOU_ART) or any(k in title_l for k in TOUHOU_TITLE):
        return '东方Project'
    if artist_hit(r, VOCALOID):
        return 'vocaloid'
    if artist_hit(r, RHYTHM):
        return '音游曲'
    if artist_hit(r, JPOP):
        return '日语动漫/流行曲'
    if artist_hit(r, EDM):
        return '欧美电音'
    if artist_hit(r, INST) or TITLE_INST.search(r['name']):
        return '纯音乐'
    return '其他'


if __name__ == '__main__':
    out = {str(r['n']): classify(r) for r in sel}
    c = Counter(out.values())
    print(dict(c), 'total', len(out))
    json.dump(out, open(os.path.join(WORK, 'cats.json'), 'w'), ensure_ascii=False, indent=0)
    print('\n=== 其他 ===')
    for r in sorted(sel, key=lambda x: x['n']):
        if out[str(r['n'])] == '其他':
            print('%d|%s|%s' % (r['n'], r['name'][:40], r['artist_str'][:34]))
