# -*- coding: utf-8 -*-
"""在页面上点播放，检查是否能播放，并抓取媒体地址。"""
import json, time, requests, websocket

targets = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type') == 'page']
t = [x for x in targets if 'y.qq.com' in x.get('url', '')][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90, suppress_origin=True)
ws.settimeout(2)
ws.send(json.dumps({'id': 1, 'method': 'Network.enable', 'params': {'maxPostDataSize': 200000}}))
ws.send(json.dumps({'id': 2, 'method': 'Page.enable'}))

urls = []


def drain(sec):
    end = time.time() + sec
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
        except Exception:
            continue
        if m.get('method') == 'Network.requestWillBeSent':
            u = m['params']['request']['url']
            if any(k in u for k in ('stream.qqmusic', '.m4a', '.mp3', '.flac', 'musicu.fcg', 'u.y.qq.com', 't.y.qq.com')):
                urls.append(u)


drain(1)
ws.send(json.dumps({'id': 3, 'method': 'Page.navigate', 'params': {'url': 'https://y.qq.com/n/ryqq/songDetail/004XzGsM308yjw'}}))
drain(9)
js = """(function(){
  var els=[...document.querySelectorAll('a,button,div')].filter(e=>/播放/.test(e.textContent||'')&&(e.className||'').toString().length<60);
  if(els.length){els[0].click(); return 'clicked:'+els[0].className;}
  return 'none';
})()"""
ws.send(json.dumps({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
drain(8)
js2 = """(function(){
  var a=document.querySelector('audio'), v=document.querySelector('video');
  var o={audio:!!a, src:a?a.src:'', t:a?a.currentTime:-1, paused:a?a.paused:null, err:a&&a.error?a.error.code:0};
  return JSON.stringify(o);
})()"""
ws.send(json.dumps({'id': 5, 'method': 'Runtime.evaluate', 'params': {'expression': js2, 'returnByValue': True}}))
while True:
    m = json.loads(ws.recv())
    if m.get('id') == 5:
        print('MEDIA:', m['result']['result'].get('value'))
        break
ws.close()
print('--- urls ---')
for u in dict.fromkeys(urls):
    print(u[:200])
