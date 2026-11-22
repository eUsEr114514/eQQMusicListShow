# -*- coding: utf-8 -*-
"""生成静态展示页：读取 SongsFiles/SongsCover 实际文件 + manifest，产出 index.html。"""
import json, os, re, html
import mutagen

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../DownloadSongs
ROOT = os.path.dirname(BASE)                                         # 项目根
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
COVERS = os.path.join(BASE, '114514Songs', 'SongsCover')
OUT = os.path.join(BASE, '114514Songs', 'index.html')

manifest = {r['n']: r for r in json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))}

tracks = []
for f in sorted(os.listdir(FILES)):
    m = re.match(r'^(\d+)-(.+)\.(mp3|flac|m4a)$', f, re.I)
    if not m:
        continue
    n = int(m.group(1))
    p = os.path.join(FILES, f)
    ext = os.path.splitext(f)[1].lower()
    size = os.path.getsize(p)
    try:
        info = mutagen.File(p).info
        dur = float(info.length)
        br = int(getattr(info, 'bitrate', 0) or 0)
    except Exception:
        dur, br = 0, 0
    if ext == '.flac':
        q = 'FLAC'
    elif br >= 300000:
        q = '320k'
    else:
        q = '128k'
    row = manifest.get(n, {})
    cover = os.path.join(COVERS, os.path.splitext(f)[0] + '.jpg')
    tracks.append({
        'n': n, 'title': row.get('name') or os.path.splitext(f)[0][len(str(n)) + 1:],
        'artist': row.get('artist_str', ''), 'album': row.get('album', ''),
        'file': os.path.splitext(f)[0], 'ext': ext, 'kb': round(size / 1024),
        'dur': round(dur), 'q': q, 'cover': os.path.exists(cover),
    })

have = {t['n'] for t in tracks}
missing = [{'n': r['n'], 'title': r['name'], 'artist': r['artist_str']}
           for n, r in sorted(manifest.items()) if r['n'] not in have]

data = {'tracks': tracks, 'missing': missing,
        'total': len(tracks) + len(missing),
        'missingCount': len(missing),
        'bytes': sum(t['kb'] for t in tracks),
        'seconds': sum(t['dur'] for t in tracks)}

payload = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

tpl = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>114514123 · 歌单漫游</title>
<style>
  :root{
    --bg:#07070b; --panel:rgba(255,255,255,.045); --line:rgba(255,255,255,.09);
    --txt:#f2f3f7; --dim:#9aa0ae; --acc:#31c27c; --acc2:#5b8cff; --hot:#ff5c8a;
    --shadow:0 24px 60px rgba(0,0,0,.55);
  }
  *{box-sizing:border-box}
  html,body{height:100%}
  body{
    margin:0; background:var(--bg); color:var(--txt); font:15px/1.5 "PingFang SC","Microsoft YaHei",system-ui,-apple-system,"Segoe UI",sans-serif;
    -webkit-font-smoothing:antialiased; overflow-x:hidden;
  }
  /* 背景光斑 */
  .aurora{position:fixed; inset:-20% -10% auto -10%; height:120vh; z-index:0; pointer-events:none; filter:blur(70px); opacity:.55}
  .aurora i{position:absolute; display:block; border-radius:50%; mix-blend-mode:screen; animation:float 18s ease-in-out infinite}
  .aurora i:nth-child(1){width:46vw;height:46vw;left:-6vw;top:-8vw;background:radial-gradient(circle,#31c27c,transparent 62%)}
  .aurora i:nth-child(2){width:38vw;height:38vw;right:2vw;top:4vw;background:radial-gradient(circle,#5b8cff,transparent 62%);animation-delay:-6s}
  .aurora i:nth-child(3){width:32vw;height:32vw;left:36vw;top:32vh;background:radial-gradient(circle,#ff5c8a,transparent 65%);animation-delay:-11s}
  @keyframes float{0%,100%{transform:translate3d(0,0,0) scale(1)}50%{transform:translate3d(3vw,4vh,0) scale(1.12)}}
  .grain{position:fixed;inset:0;z-index:1;pointer-events:none;opacity:.035;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}

  .wrap{position:relative; z-index:2; max-width:1400px; margin:0 auto; padding:34px 26px 190px}

  header.top{display:flex; gap:26px; align-items:flex-end; flex-wrap:wrap; margin-bottom:26px}
  .brand{display:flex; align-items:center; gap:14px}
  .logo{width:54px;height:54px;border-radius:16px;background:linear-gradient(135deg,var(--acc),#1aa06a 60%,#0d7a4f);
    display:grid;place-items:center;font-weight:800;font-size:22px;color:#04170f;box-shadow:0 10px 30px rgba(49,194,124,.35)}
  h1{margin:0;font-size:clamp(26px,3.4vw,44px);letter-spacing:-.02em;line-height:1.05;
     background:linear-gradient(100deg,#fff 10%,#9ff5c9 45%,#8fb4ff 85%);-webkit-background-clip:text;background-clip:text;color:transparent}
  .sub{margin:6px 0 0;color:var(--dim);font-size:13.5px;letter-spacing:.04em}
  .stats{display:flex;gap:26px;margin-left:auto;flex-wrap:wrap}
  .stat b{display:block;font-size:20px;font-weight:700;font-variant-numeric:tabular-nums}
  .stat span{font-size:11.5px;color:var(--dim);letter-spacing:.14em;text-transform:uppercase}

  .toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:18px 0 22px;
    padding:12px;border:1px solid var(--line);border-radius:18px;background:var(--panel);backdrop-filter:blur(18px)}
  .search{position:relative;flex:1 1 280px;min-width:220px}
  .search svg{position:absolute;left:14px;top:50%;transform:translateY(-50%);opacity:.5}
  #q{width:100%;padding:13px 14px 13px 42px;border-radius:12px;border:1px solid var(--line);
     background:rgba(0,0,0,.35);color:var(--txt);font-size:14px;outline:none;transition:.22s}
  #q:focus{border-color:rgba(49,194,124,.6);box-shadow:0 0 0 4px rgba(49,194,124,.12)}
  .chips{display:flex;gap:8px;flex-wrap:wrap}
  .chip{padding:9px 14px;border-radius:11px;border:1px solid var(--line);background:rgba(255,255,255,.03);
    color:var(--dim);font-size:13px;cursor:pointer;transition:.18s;user-select:none;white-space:nowrap}
  .chip:hover{color:#fff;border-color:rgba(255,255,255,.24);transform:translateY(-1px)}
  .chip.on{background:linear-gradient(135deg,rgba(49,194,124,.22),rgba(91,140,255,.18));color:#fff;
    border-color:rgba(49,194,124,.55);box-shadow:0 6px 22px rgba(49,194,124,.16)}
  select#sort{padding:11px 12px;border-radius:11px;border:1px solid var(--line);background:rgba(0,0,0,.35);
    color:var(--txt);font-size:13px;outline:none;cursor:pointer}
  .btn{display:inline-flex;align-items:center;gap:8px;padding:11px 16px;border-radius:11px;border:0;cursor:pointer;
    font-size:13.5px;font-weight:600;color:#04170f;background:linear-gradient(135deg,#43e39a,#31c27c);
    box-shadow:0 10px 26px rgba(49,194,124,.26);transition:.18s}
  .btn:hover{transform:translateY(-1px);filter:brightness(1.06)}
  .btn.ghost{background:rgba(255,255,255,.06);color:var(--txt);box-shadow:none;border:1px solid var(--line)}

  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:18px}
  .card{position:relative;border-radius:16px;overflow:hidden;background:var(--panel);border:1px solid var(--line);
    cursor:pointer;transition:transform .22s cubic-bezier(.2,.7,.3,1),box-shadow .22s,border-color .22s;
    transform:translateZ(0)}
  .card:hover{transform:translateY(-6px);box-shadow:var(--shadow);border-color:rgba(255,255,255,.2)}
  .cover{position:relative;aspect-ratio:1/1;background:#111318;overflow:hidden}
  .cover img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s ease,filter .3s;filter:saturate(1.05)}
  .card:hover .cover img{transform:scale(1.06)}
  .cover .ph{position:absolute;inset:0;display:grid;place-items:center;font-size:34px;color:#2b2f39}
  .play{position:absolute;right:10px;bottom:10px;width:40px;height:40px;border-radius:50%;display:grid;place-items:center;
    background:rgba(10,12,16,.62);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.18);
    opacity:0;transform:translateY(8px) scale(.9);transition:.22s}
  .card:hover .play,.card.on .play{opacity:1;transform:none}
  .card.on{border-color:rgba(49,194,124,.65);box-shadow:0 0 0 1px rgba(49,194,124,.35),0 18px 44px rgba(49,194,124,.16)}
  .meta{padding:11px 12px 13px}
  .t{font-size:13.5px;font-weight:600;line-height:1.35;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;
    overflow:hidden;min-height:37px}
  .a{margin-top:5px;font-size:11.5px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .tags{display:flex;gap:6px;margin-top:8px;align-items:center}
  .badge{font-size:10px;letter-spacing:.06em;padding:2.5px 6px;border-radius:6px;border:1px solid var(--line);color:var(--dim)}
  .badge.flac{color:#8ff0c0;border-color:rgba(49,194,124,.45);background:rgba(49,194,124,.1)}
  .badge.q320{color:#a9c2ff;border-color:rgba(91,140,255,.4);background:rgba(91,140,255,.1)}
  .badge.q128{color:#ffd08a;border-color:rgba(255,180,80,.35);background:rgba(255,180,80,.08)}
  .badge.miss{color:#ff9bb4;border-color:rgba(255,92,138,.4);background:rgba(255,92,138,.1)}
  .card.missing{opacity:.42;cursor:not-allowed}
  .card.missing:hover{transform:none;box-shadow:none}

  .eq{position:absolute;left:10px;top:10px;display:none;gap:2.5px;align-items:flex-end;height:16px;
    padding:4px 6px;border-radius:7px;background:rgba(10,12,16,.6);backdrop-filter:blur(8px)}
  .card.on .eq{display:flex}
  .eq i{display:block;width:3px;background:#43e39a;border-radius:2px;animation:bar .9s ease-in-out infinite}
  .eq i:nth-child(2){animation-delay:.15s}.eq i:nth-child(3){animation-delay:.3s}.eq i:nth-child(4){animation-delay:.45s}
  @keyframes bar{0%,100%{height:4px}50%{height:14px}}

  .empty{padding:80px 10px;text-align:center;color:var(--dim)}
  .sentinel{height:60px}

  /* 播放器 */
  .player{position:fixed;left:0;right:0;bottom:0;z-index:20;padding:12px 18px calc(12px + env(safe-area-inset-bottom));
    background:linear-gradient(180deg,rgba(8,9,13,.72),rgba(8,9,13,.94));backdrop-filter:blur(24px) saturate(1.2);
    border-top:1px solid rgba(255,255,255,.08);box-shadow:0 -18px 50px rgba(0,0,0,.5)}
  .pinner{max-width:1400px;margin:0 auto;display:grid;grid-template-columns:minmax(180px,1.1fr) 2.2fr minmax(140px,.9fr);
    gap:18px;align-items:center}
  .now{display:flex;gap:12px;align-items:center;min-width:0}
  .now img{width:52px;height:52px;border-radius:10px;object-fit:cover;background:#15171d;flex:none}
  .now .txt{min-width:0}
  .now .n1{font-size:13.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .now .n2{font-size:11.5px;color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:3px}
  .center{display:flex;flex-direction:column;gap:6px;align-items:center}
  .ctrls{display:flex;align-items:center;gap:14px}
  .ib{width:38px;height:38px;border-radius:50%;border:1px solid transparent;background:transparent;color:#cfd3dc;
    cursor:pointer;display:grid;place-items:center;transition:.16s}
  .ib:hover{color:#fff;background:rgba(255,255,255,.08)}
  .ib.big{width:46px;height:46px;background:linear-gradient(135deg,#43e39a,#31c27c);color:#04170f;
    box-shadow:0 8px 24px rgba(49,194,124,.35)}
  .ib.big:hover{filter:brightness(1.08)}
  .ib.on{color:#43e39a}
  .bar{display:flex;align-items:center;gap:10px;width:100%}
  .time{font-size:11px;color:var(--dim);font-variant-numeric:tabular-nums;min-width:38px;text-align:center}
  .track{position:relative;flex:1;height:5px;border-radius:4px;background:rgba(255,255,255,.12);cursor:pointer}
  .track .buf{position:absolute;inset:0;width:0;background:rgba(255,255,255,.18);border-radius:4px}
  .track .prog{position:absolute;inset:0;width:0;border-radius:4px;background:linear-gradient(90deg,#31c27c,#7dd3fc)}
  .track .knob{position:absolute;top:50%;left:0;width:12px;height:12px;margin-left:-6px;border-radius:50%;background:#fff;
    transform:translateY(-50%) scale(0);transition:transform .16s;box-shadow:0 0 0 4px rgba(49,194,124,.2)}
  .track:hover .knob{transform:translateY(-50%) scale(1)}
  .right{display:flex;align-items:center;gap:10px;justify-content:flex-end}
  .vol{width:92px;height:4px;border-radius:4px;background:rgba(255,255,255,.14);position:relative;cursor:pointer}
  .vol i{position:absolute;inset:0;width:80%;border-radius:4px;background:rgba(255,255,255,.6)}
  .hint{position:fixed;left:50%;top:22px;transform:translate(-50%,-16px);z-index:40;padding:10px 16px;border-radius:12px;
    background:rgba(16,18,24,.92);border:1px solid var(--line);color:#e8eaf0;font-size:13px;opacity:0;transition:.25s;pointer-events:none}
  .hint.show{opacity:1;transform:translate(-50%,0)}
  @media (max-width:820px){
    .pinner{grid-template-columns:1fr;gap:10px}
    .right{display:none}
    .now img{width:42px;height:42px}
    .wrap{padding:22px 16px 210px}
    .grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:12px}
  }
</style>
</head>
<body>
<div class="aurora"><i></i><i></i><i></i></div>
<div class="grain"></div>

<div class="wrap">
  <header class="top">
    <div class="brand">
      <div class="logo">♪</div>
      <div>
        <h1>114514123</h1>
        <p class="sub">QQ音乐歌单 · 本地音频漫游 · <span id="cnt"></span></p>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><b id="s1"></b><span>曲目</span></div>
      <div class="stat"><b id="s2"></b><span>总时长</span></div>
      <div class="stat"><b id="s3"></b><span>体积</span></div>
    </div>
  </header>

  <div class="toolbar">
    <div class="search">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="q" placeholder="搜索歌名 / 歌手 / 专辑   （按 / 聚焦）" autocomplete="off">
    </div>
    <div class="chips" id="chips">
      <div class="chip on" data-f="all">全部</div>
      <div class="chip" data-f="flac">FLAC</div>
      <div class="chip" data-f="320k">320k</div>
      <div class="chip" data-f="128k">128k</div>
      <div class="chip" data-f="miss">缺源</div>
    </div>
    <select id="sort">
      <option value="n">歌单顺序</option>
      <option value="name">歌名 A→Z</option>
      <option value="dur">时长</option>
      <option value="size">体积</option>
    </select>
    <button class="btn" id="shuffle">随机播放</button>
  </div>

  <div class="grid" id="grid"></div>
  <div class="empty" id="empty" style="display:none">没有匹配的曲目</div>
  <div class="sentinel" id="sentinel"></div>
</div>

<div class="player">
  <div class="pinner">
    <div class="now">
      <img id="pcover" alt="" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='52' height='52'%3E%3Crect width='52' height='52' fill='%23161820'/%3E%3C/svg%3E">
      <div class="txt">
        <div class="n1" id="ptitle">未在播放</div>
        <div class="n2" id="partist">点击任意封面开始</div>
      </div>
    </div>
    <div class="center">
      <div class="ctrls">
        <button class="ib" id="prev" title="上一首 (←)"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 5h2v14H6zM20 5v14l-11-7z"/></svg></button>
        <button class="ib big" id="toggle" title="播放/暂停 (空格)"><svg id="icoplay" width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></button>
        <button class="ib" id="next" title="下一首 (→)"><svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16 5h2v14h-2zM4 5v14l11-7z"/></svg></button>
        <button class="ib" id="mode" title="播放模式"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 2l4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="M7 22l-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg></button>
      </div>
      <div class="bar">
        <span class="time" id="cur">0:00</span>
        <div class="track" id="track"><div class="buf" id="buf"></div><div class="prog" id="prog"></div><div class="knob" id="knob"></div></div>
        <span class="time" id="tot">0:00</span>
      </div>
    </div>
    <div class="right">
      <button class="ib" id="mute" title="静音"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 5 6 9H3v6h3l5 4z"/><path d="M16 9a4 4 0 0 1 0 6"/></svg></button>
      <div class="vol" id="vol"><i id="voli"></i></div>
    </div>
  </div>
</div>
<div class="hint" id="hint"></div>

<script>
const DATA = __DATA__;
const $ = s => document.querySelector(s);
const tracks = DATA.tracks;
const all = tracks.concat(DATA.missing.map(m => ({n:m.n, title:m.title, artist:m.artist, album:'', file:'', ext:'', kb:0, dur:0, q:'miss', cover:false})));
all.sort((a,b)=>a.n-b.n);

const fmt = s => { s=Math.max(0,Math.floor(s||0)); const m=Math.floor(s/60); const x=s%60; return m+':'+String(x).padStart(2,'0'); };
const enc = p => p.split('/').map(encodeURIComponent).join('/');

$('#cnt').textContent = '已收录 ' + tracks.length + ' 首 / 共 ' + DATA.total + ' 首';
$('#s1').textContent = tracks.length;
$('#s2').textContent = Math.floor(DATA.seconds/3600) + 'h' + Math.round(DATA.seconds%3600/60) + 'm';
$('#s3').textContent = (DATA.bytes/1048576).toFixed(1) + 'G';

let filter='all', kw='', sortKey='n', shown=0, filtered=[], queue=[], qi=-1;
const PAGE=140;
const grid=$('#grid'), sentinel=$('#sentinel'), empty=$('#empty');
const audio=new Audio(); audio.preload='metadata'; audio.volume=0.85;

function apply(){
  kw=$('#q').value.trim().toLowerCase();
  filtered = all.filter(t=>{
    if(filter==='miss') return t.q==='miss';
    if(filter!=='all' && t.q!==filter) return false;
    if(!kw) return true;
    return (t.title+' '+t.artist+' '+t.album).toLowerCase().includes(kw);
  });
  if(sortKey==='name') filtered.sort((a,b)=>a.title.localeCompare(b.title,'zh'));
  else if(sortKey==='dur') filtered.sort((a,b)=>b.dur-a.dur);
  else if(sortKey==='size') filtered.sort((a,b)=>b.kb-a.kb);
  else filtered.sort((a,b)=>a.n-b.n);
  grid.innerHTML=''; shown=0; empty.style.display=filtered.length?'none':'block';
  renderMore();
  queue = filtered.filter(t=>t.q!=='miss');
}

function renderMore(){
  const frag=document.createDocumentFragment();
  const end=Math.min(shown+PAGE, filtered.length);
  for(let i=shown;i<end;i++) frag.appendChild(card(filtered[i]));
  grid.appendChild(frag); shown=end;
}

function card(t){
  const el=document.createElement('div');
  el.className='card'+(t.q==='miss'?' missing':'');
  el.dataset.n=t.n;
  const cov = t.cover ? enc('SongsCover/'+t.file+'.jpg') : '';
  const badge = t.q==='miss' ? '<span class="badge miss">缺源</span>'
    : '<span class="badge '+(t.q==='FLAC'?'flac':t.q==='320k'?'q320':'q128')+'">'+t.q+'</span>';
  el.innerHTML =
    '<div class="cover">'+
      (cov?'<img loading="lazy" src="'+cov+'" alt="">':'<div class="ph">♪</div>')+
      '<div class="eq"><i></i><i></i><i></i><i></i></div>'+
      (t.q!=='miss'?'<div class="play"><svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><path d="M8 5v14l11-7z"/></svg></div>':'')+
    '</div>'+
    '<div class="meta"><div class="t">'+esc(t.title)+'</div>'+
    '<div class="a">'+esc(t.artist||'未知歌手')+'</div>'+
    '<div class="tags">'+badge+'<span class="badge">'+fmt(t.dur)+'</span>'+
      (t.kb?'<span class="badge">'+(t.kb/1024).toFixed(1)+'M</span>':'')+'</div></div>';
  el.addEventListener('click',()=>{
    if(t.q==='miss'){ toast('第 '+t.n+' 首暂缺音频源'); return; }
    const idx=queue.findIndex(x=>x.n===t.n);
    if(idx<0){ queue=filtered.filter(x=>x.q!=='miss'); }
    playAt(queue.findIndex(x=>x.n===t.n));
  });
  return el;
}
function esc(s){ return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }

function playAt(i){
  if(i<0||i>=queue.length) return;
  qi=i; const t=queue[i];
  audio.src=enc('SongsFiles/'+t.file+t.ext);
  audio.play().catch(()=>toast('浏览器阻止了自动播放，请再点一次'));
  $('#ptitle').textContent=t.title;
  $('#partist').textContent=t.artist||'未知歌手';
  const cov=t.cover?enc('SongsCover/'+t.file+'.jpg'):'';
  $('#pcover').src=cov||$('#pcover').src;
  document.querySelectorAll('.card.on').forEach(e=>e.classList.remove('on'));
  const el=document.querySelector('.card[data-n="'+t.n+'"]');
  if(el){ el.classList.add('on'); el.scrollIntoView({block:'nearest',behavior:'smooth'}); }
  localStorage.setItem('qmp',JSON.stringify({n:t.n,vol:audio.volume,mode}));
  document.title=t.title+' · 114514123';
}

let mode=0; // 0 顺序 1 单曲 2 随机
audio.addEventListener('ended',()=>{
  if(mode===1){ audio.currentTime=0; audio.play(); return; }
  if(mode===2){ playAt(Math.floor(Math.random()*queue.length)); return; }
  playAt(qi+1<queue.length?qi+1:0);
});
audio.addEventListener('timeupdate',()=>{
  const d=audio.duration||0;
  $('#prog').style.width=d?(audio.currentTime/d*100)+'%':'0';
  $('#knob').style.left=d?(audio.currentTime/d*100)+'%':'0';
  $('#cur').textContent=fmt(audio.currentTime);
  $('#tot').textContent=fmt(d);
});
audio.addEventListener('play',()=>{ $('#icoplay').innerHTML='<path d="M7 5h4v14H7zM13 5h4v14h-4z"/>'; });
audio.addEventListener('pause',()=>{ $('#icoplay').innerHTML='<path d="M8 5v14l11-7z"/>'; });
audio.addEventListener('error',()=>{ if(audio.src) toast('该文件无法播放'); });

$('#toggle').onclick=()=>{ if(!audio.src){ playAt(0); return; } audio.paused?audio.play():audio.pause(); };
$('#next').onclick=()=>playAt(qi+1<queue.length?qi+1:0);
$('#prev').onclick=()=>playAt(qi-1>=0?qi-1:queue.length-1);
$('#mode').onclick=()=>{ mode=(mode+1)%3; $('#mode').classList.toggle('on',mode>0);
  toast(['顺序播放','单曲循环','随机播放'][mode]); localStorage.setItem('qmmode',mode); };
$('#shuffle').onclick=()=>{ if(!queue.length) return; playAt(Math.floor(Math.random()*queue.length)); };
$('#track').addEventListener('click',e=>{
  const r=e.currentTarget.getBoundingClientRect();
  const p=Math.min(1,Math.max(0,(e.clientX-r.left)/r.width));
  if(audio.duration) audio.currentTime=p*audio.duration;
});
$('#vol').addEventListener('click',e=>{
  const r=e.currentTarget.getBoundingClientRect();
  setVol(Math.min(1,Math.max(0,(e.clientX-r.left)/r.width)));
});
function setVol(v){ audio.volume=v; audio.muted=v===0; $('#voli').style.width=(v*100)+'%';
  $('#mute').classList.toggle('on',v===0); localStorage.setItem('qmvol',v); }
$('#mute').onclick=()=>{ if(audio.volume>0){ lastVol=audio.volume; setVol(0);} else setVol(lastVol||0.85); };
let lastVol=0.85;

$('#chips').addEventListener('click',e=>{
  const c=e.target.closest('.chip'); if(!c) return;
  document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on'));
  c.classList.add('on'); filter=c.dataset.f; apply();
});
$('#q').addEventListener('input',()=>{ clearTimeout(window._t); window._t=setTimeout(apply,120); });
$('#sort').addEventListener('change',e=>{ sortKey=e.target.value; apply(); });

new IntersectionObserver(es=>{ if(es[0].isIntersecting && shown<filtered.length) renderMore(); },
  {rootMargin:'600px'}).observe(sentinel);

document.addEventListener('keydown',e=>{
  if(e.target.tagName==='INPUT'||e.target.tagName==='SELECT') { if(e.key==='Escape') e.target.blur(); return; }
  if(e.code==='Space'){ e.preventDefault(); $('#toggle').click(); }
  if(e.key==='ArrowRight'){ e.preventDefault(); $('#next').click(); }
  if(e.key==='ArrowLeft'){ e.preventDefault(); $('#prev').click(); }
  if(e.key==='ArrowUp'){ e.preventDefault(); setVol(Math.min(1,audio.volume+0.05)); }
  if(e.key==='ArrowDown'){ e.preventDefault(); setVol(Math.max(0,audio.volume-0.05)); }
  if(e.key==='/'){ e.preventDefault(); $('#q').focus(); }
});

let hintT;
function toast(msg){ const h=$('#hint'); h.textContent=msg; h.classList.add('show');
  clearTimeout(hintT); hintT=setTimeout(()=>h.classList.remove('show'),1800); }

// 恢复上次状态
try{
  const v=parseFloat(localStorage.getItem('qmvol')); if(!isNaN(v)) setVol(v);
  const m=parseInt(localStorage.getItem('qmmode')||'0'); mode=m; $('#mode').classList.toggle('on',m>0);
  const p=JSON.parse(localStorage.getItem('qmp')||'{}');
  if(p.n){ const t=all.find(x=>x.n===p.n && x.q!=='miss');
    if(t){ $('#ptitle').textContent=t.title; $('#partist').textContent=t.artist;
      if(t.cover) $('#pcover').src=enc('SongsCover/'+t.file+'.jpg'); } }
}catch(e){}

apply();
</script>
</body>
</html>
'''

html_out = tpl.replace('__DATA__', payload)
open(OUT, 'w', encoding='utf-8').write(html_out)
print('wrote', OUT, '%.1f KB' % (os.path.getsize(OUT) / 1024))
print('tracks', len(tracks), 'missing', len(missing))
