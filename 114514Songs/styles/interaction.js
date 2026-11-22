(function(){
    'use strict';
    const P = window.PLAYLIST;
    const tracks = P.tracks;
    const $ = s => document.querySelector(s);
    const enc = p => p.split('/').map(encodeURIComponent).join('/');
    const fmt = s => { s = Math.max(0, Math.floor(s || 0)); return Math.floor(s/60) + ':' + String(s%60).padStart(2,'0'); };

    /* ---------- 头部信息 ---------- */
    $('#siteTitle').textContent = P.meta.title;
    $('#siteSub').textContent = P.meta.subtitle;
    $('#cnt').textContent = P.meta.count;
    $('#s1').textContent = P.meta.count;
    $('#s2').textContent = Math.floor(P.meta.seconds/3600) + 'h' + Math.round(P.meta.seconds%3600/60) + 'm';
    $('#s3').textContent = (P.meta.kb/1048576).toFixed(1) + 'G';

    /* ---------- 分类计数 ---------- */
    const counts = { '全部': tracks.length };
    tracks.forEach(t => counts[t.cat] = (counts[t.cat] || 0) + 1);
    document.querySelectorAll('[data-count]').forEach(el => {
        el.textContent = counts[el.dataset.count] || 0;
    });

    /* ---------- 状态 ---------- */
    let cat = '全部', kw = '', sortKey = 'default';
    let filtered = [], queue = [], qi = -1, shown = 0, mode = 0;
    const PAGE = 140;
    const grid = $('#grid'), sentinel = $('#sentinel'), empty = $('#empty');
    const audio = new Audio();
    audio.preload = 'metadata';
    audio.volume = 0.85;

    /* ---------- 渲染 ---------- */
    function apply(){
        kw = $('#q').value.trim().toLowerCase();
        filtered = tracks.filter(t => {
            if (cat !== '全部' && t.cat !== cat) return false;
            if (!kw) return true;
            return (t.title + ' ' + t.artist + ' ' + t.album).toLowerCase().includes(kw);
        });
        if (sortKey === 'name') filtered.sort((a,b) => a.title.localeCompare(b.title, 'zh'));
        else if (sortKey === 'dur') filtered.sort((a,b) => b.dur - a.dur);
        else if (sortKey === 'size') filtered.sort((a,b) => b.kb - a.kb);
        /* default：保持 data/tracks.js 里的数组顺序 —— 想置顶就把条目放到数组最前面 */

        grid.innerHTML = '';
        shown = 0;
        empty.style.display = filtered.length ? 'none' : 'block';
        renderMore();
        queue = filtered;
    }

    function renderMore(){
        const frag = document.createDocumentFragment();
        const end = Math.min(shown + PAGE, filtered.length);
        for (let i = shown; i < end; i++) frag.appendChild(card(filtered[i]));
        grid.appendChild(frag);
        shown = end;
    }

    function esc(s){
        return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
    }

    function card(t){
        const el = document.createElement('div');
        el.className = 'card';
        el.dataset.n = t.n;
        const cov = t.cover ? enc('SongsCover/' + t.file + '.jpg') : '';
        const qCls = t.q === 'FLAC' ? 'flac' : (t.q === '320k' ? 'q320' : 'q128');
        el.innerHTML =
            '<div class="cover">' +
            (cov ? '<img loading="lazy" src="' + cov + '" alt="">' : '<div class="ph">♪</div>') +
            '<span class="cat-pill">' + esc(t.cat) + '</span>' +
            '<div class="eq"><i></i><i></i><i></i><i></i></div>' +
            '<div class="play"><svg width="16" height="16" viewBox="0 0 24 24" fill="#fff"><path d="M8 5v14l11-7z"/></svg></div>' +
            '</div>' +
            '<div class="meta">' +
            '<div class="t" title="' + esc(t.title) + '">' + esc(t.title) + '</div>' +
            '<div class="a" title="' + esc(t.artist) + '">' + esc(t.artist || '未知歌手') + '</div>' +
            '<div class="tags">' +
            '<span class="badge ' + qCls + '">' + t.q + '</span>' +
            '<span class="badge">' + fmt(t.dur) + '</span>' +
            '<span class="badge">' + (t.kb / 1024).toFixed(1) + 'M</span>' +
            '</div>' +
            '</div>';
        el.addEventListener('click', () => {
            const idx = queue.findIndex(x => x.n === t.n);
            playAt(idx >= 0 ? idx : 0);
        });
        return el;
    }

    /* ---------- 播放 ---------- */
    function playAt(i){
        if (i < 0 || i >= queue.length) return;
        qi = i;
        const t = queue[i];
        audio.src = enc('SongsFiles/' + t.file + t.ext);
        audio.play().catch(() => toast('浏览器拦截了自动播放，再点一次即可'));
        $('#ptitle').textContent = t.title;
        $('#partist').textContent = (t.artist || '未知歌手') + ' · ' + t.cat;
        if (t.cover) $('#pcover').src = enc('SongsCover/' + t.file + '.jpg');
        document.querySelectorAll('.card.on').forEach(e => e.classList.remove('on'));
        const el = document.querySelector('.card[data-n="' + t.n + '"]');
        if (el){ el.classList.add('on'); el.scrollIntoView({block:'nearest', behavior:'smooth'}); }
        document.title = t.title + ' · ' + P.meta.title;
        try { localStorage.setItem('qm_last', t.n); } catch(e){}
    }

    audio.addEventListener('ended', () => {
        if (mode === 1){ audio.currentTime = 0; audio.play(); return; }
        if (mode === 2){ playAt(Math.floor(Math.random() * queue.length)); return; }
        playAt(qi + 1 < queue.length ? qi + 1 : 0);
    });
    audio.addEventListener('timeupdate', () => {
        const d = audio.duration || 0;
        const p = d ? (audio.currentTime / d * 100) : 0;
        $('#prog').style.width = p + '%';
        $('#knob').style.left = p + '%';
        $('#cur').textContent = fmt(audio.currentTime);
        $('#tot').textContent = fmt(d);
    });
    audio.addEventListener('play', () => { $('#icoplay').innerHTML = '<path d="M7 5h4v14H7zM13 5h4v14h-4z"/>'; });
    audio.addEventListener('pause', () => { $('#icoplay').innerHTML = '<path d="M8 5v14l11-7z"/>'; });
    audio.addEventListener('error', () => { if (audio.src) toast('该文件无法播放'); });

    /* ---------- 控件 ---------- */
    $('#toggle').onclick = () => {
        if (!audio.src){ playAt(0); return; }
        audio.paused ? audio.play() : audio.pause();
    };
    $('#next').onclick = () => playAt(qi + 1 < queue.length ? qi + 1 : 0);
    $('#prev').onclick = () => playAt(qi - 1 >= 0 ? qi - 1 : queue.length - 1);
    $('#mode').onclick = () => {
        mode = (mode + 1) % 3;
        $('#mode').classList.toggle('on', mode > 0);
        toast(['顺序播放', '单曲循环', '随机播放'][mode]);
        try { localStorage.setItem('qm_mode', mode); } catch(e){}
    };
    $('#shuffle').onclick = () => {
        if (!queue.length) return;
        playAt(Math.floor(Math.random() * queue.length));
    };
    $('#track').addEventListener('click', e => {
        const r = e.currentTarget.getBoundingClientRect();
        const p = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width));
        if (audio.duration) audio.currentTime = p * audio.duration;
    });
    $('#vol').addEventListener('click', e => {
        const r = e.currentTarget.getBoundingClientRect();
        setVol(Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)));
    });
    let lastVol = 0.85;
    function setVol(v){
        audio.volume = v;
        audio.muted = v === 0;
        $('#voli').style.width = (v * 100) + '%';
        $('#mute').classList.toggle('on', v === 0);
        try { localStorage.setItem('qm_vol', v); } catch(e){}
    }
    $('#mute').onclick = () => {
        if (audio.volume > 0){ lastVol = audio.volume; setVol(0); }
        else setVol(lastVol || 0.85);
    };

    /* ---------- 筛选 / 搜索 / 排序 ---------- */
    $('#chips').addEventListener('click', e => {
        const c = e.target.closest('.chip');
        if (!c) return;
        document.querySelectorAll('.chip').forEach(x => x.classList.remove('on'));
        c.classList.add('on');
        cat = c.dataset.cat;
        apply();
    });
    $('#q').addEventListener('input', () => {
        clearTimeout(window._t);
        window._t = setTimeout(apply, 120);
    });
    $('#sort').addEventListener('change', e => {
        sortKey = e.target.value;
        apply();
    });

    /* ---------- 懒加载 ---------- */
    new IntersectionObserver(es => {
        if (es[0].isIntersecting && shown < filtered.length) renderMore();
    }, {rootMargin:'600px'}).observe(sentinel);

    /* ---------- 快捷键 ---------- */
    document.addEventListener('keydown', e => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT'){
            if (e.key === 'Escape') e.target.blur();
            return;
        }
        if (e.code === 'Space'){ e.preventDefault(); $('#toggle').click(); }
        else if (e.key === 'ArrowRight'){ e.preventDefault(); $('#next').click(); }
        else if (e.key === 'ArrowLeft'){ e.preventDefault(); $('#prev').click(); }
        else if (e.key === 'ArrowUp'){ e.preventDefault(); setVol(Math.min(1, audio.volume + 0.05)); }
        else if (e.key === 'ArrowDown'){ e.preventDefault(); setVol(Math.max(0, audio.volume - 0.05)); }
        else if (e.key === '/'){ e.preventDefault(); $('#q').focus(); }
    });

    /* ---------- 提示 ---------- */
    let hintT;
    function toast(msg){
        const h = $('#hint');
        h.textContent = msg;
        h.classList.add('show');
        clearTimeout(hintT);
        hintT = setTimeout(() => h.classList.remove('show'), 1800);
    }

    /* ---------- 恢复上次状态 ---------- */
    try {
        const v = parseFloat(localStorage.getItem('qm_vol'));
        if (!isNaN(v)) setVol(v);
        const m = parseInt(localStorage.getItem('qm_mode') || '0', 10);
        mode = m; $('#mode').classList.toggle('on', m > 0);
        const lastN = parseInt(localStorage.getItem('qm_last') || '0', 10);
        const t = tracks.find(x => x.n === lastN);
        if (t){
            $('#ptitle').textContent = t.title;
            $('#partist').textContent = t.artist + ' · ' + t.cat;
            if (t.cover) $('#pcover').src = enc('SongsCover/' + t.file + '.jpg');
        }
    } catch(e){}

    apply();
})();