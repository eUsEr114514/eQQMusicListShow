# -*- coding: utf-8 -*-
"""在 gequbao 页面上走一次下载流程，抓取真实接口与响应。"""
import json, time, requests, websocket

t = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json()
     if x.get('type') == 'page' and 'gequbao' in x.get('url', '')][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=120, suppress_origin=True)
ws.settimeout(2)
ws.send(json.dumps({'id': 1, 'method': 'Network.enable', 'params': {'maxPostDataSize': 200000}}))
ws.send(json.dumps({'id': 2, 'method': 'Page.enable'}))
count = [10]
hits = []


def send(method, params):
    count[0] += 1
    ws.send(json.dumps({'id': count[0], 'method': method, 'params': params}))
    return count[0]


def drain(sec):
    end = time.time() + sec
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
        except Exception:
            continue
        if m.get('method') == 'Network.requestWillBeSent':
            u = m['params']['request']['url']
            if '/api/' in u or 'play-url' in u or 'download' in u or '.mp3' in u or '.flac' in u:
                hits.append(('REQ', u, (m['params']['request'].get('postData') or '')[:200]))
        elif m.get('method') == 'Network.responseReceived':
            u = m['params'].get('response', {}).get('url', '')
            if '/api/' in u or 'play-url' in u or 'download' in u:
                hits.append(('RESP', u, m['params']['response'].get('status')))


drain(1)
# 1) 搜索
i = send('Runtime.evaluate', {'expression': '''(async()=>{
  const r=await fetch("/search-fallback?keyword="+encodeURIComponent("刚好遇见你"));
  const t=await r.text();
  const m=t.match(/\\/music\\/(\\d+)/);
  return m?m[1]:'none';
})()''', 'awaitPromise': True, 'returnByValue': True})
sid = None
end = time.time() + 20
while time.time() < end:
    try:
        m = json.loads(ws.recv())
    except Exception:
        continue
    if m.get('id') == i:
        sid = (m.get('result', {}).get('result', {}) or {}).get('value')
        break
print('song id', sid)
if not sid or sid == 'none':
    raise SystemExit
send('Page.navigate', {'url': 'https://www.gequbao.com/music/%s' % sid})
drain(9)
i = send('Runtime.evaluate', {'expression': '''(function(){
  const b=document.querySelector('.btn-download-mp3');
  if(!b) return 'no btn';
  b.click(); return 'clicked ' + b.className;
})()''', 'returnByValue': True})
end = time.time() + 8
while time.time() < end:
    try:
        m = json.loads(ws.recv())
    except Exception:
        continue
    if m.get('id') == i:
        print('click:', m.get('result', {}).get('result', {}).get('value'))
        break
drain(10)
ws.close()
for h in hits[:20]:
    print(h)
