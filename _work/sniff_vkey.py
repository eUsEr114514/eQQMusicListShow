# -*- coding: utf-8 -*-
"""监听页面网络请求：抓取站点自身调用 vkey 接口的参数与响应。"""
import json, time, requests, websocket

targets = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type') == 'page']
t = [x for x in targets if 'y.qq.com' in x.get('url', '')][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90, suppress_origin=True)
ws.settimeout(2)
ws.send(json.dumps({'id': 1, 'method': 'Network.enable', 'params': {'maxPostDataSize': 20000}}))
ws.send(json.dumps({'id': 2, 'method': 'Page.enable'}))

reqs = {}
hits = []


def drain(seconds):
    end = time.time() + seconds
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
        except Exception:
            continue
        meth = m.get('method')
        if meth == 'Network.requestWillBeSent':
            p = m['params']
            reqs[p['requestId']] = p['request']
            if 'musicu.fcg' in p['request']['url'] or 'vkey' in p['request']['url']:
                hits.append(('REQ', p['request']['url'], p['request'].get('postData')))
        elif meth == 'Network.responseReceived':
            p = m['params']
            u = p.get('response', {}).get('url', '')
            if 'musicu.fcg' in u or 'vkey' in u:
                hits.append(('RESP', u, p['response'].get('status')))


drain(1)
ws.send(json.dumps({'id': 3, 'method': 'Page.navigate', 'params': {'url': 'https://y.qq.com/n/ryqq/songDetail/004XzGsM308yjw'}}))
drain(8)
js = """(function(){
  var btn = document.querySelector('.mod_btn_green') || document.querySelector('.song_detail__play') || document.querySelector('[class*=play]');
  if (btn) { btn.click(); return 'clicked ' + btn.className; }
  return 'no button';
})()"""
ws.send(json.dumps({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
drain(10)
ws.close()

for kind, url, extra in hits:
    print(kind, url[:120])
    if extra:
        print('   ', str(extra)[:900])
