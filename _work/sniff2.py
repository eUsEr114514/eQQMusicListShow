# -*- coding: utf-8 -*-
"""抓取 t.y.qq.com musicu.fcg 的完整请求与响应体。"""
import json, time, requests, websocket, urllib.parse

targets = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type') == 'page']
t = [x for x in targets if 'y.qq.com' in x.get('url', '')][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=90, suppress_origin=True)
ws.settimeout(2)
ws.send(json.dumps({'id': 1, 'method': 'Network.enable', 'params': {'maxPostDataSize': 200000, 'maxTotalBufferSize': 50000000}}))
ws.send(json.dumps({'id': 2, 'method': 'Page.enable'}))

seen = {}


def drain(seconds):
    end = time.time() + seconds
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
        except Exception:
            continue
        if m.get('method') == 'Network.requestWillBeSent':
            p = m['params']
            r = p['request']
            if 'musicu.fcg' in r['url']:
                seen[p['requestId']] = r
        elif m.get('method') == 'Network.loadingFinished':
            rid = m['params']['requestId']
            if rid in seen:
                ws.send(json.dumps({'id': 99, 'method': 'Network.getResponseBody', 'params': {'requestId': rid}}))


drain(1)
ws.send(json.dumps({'id': 3, 'method': 'Page.navigate', 'params': {'url': 'https://y.qq.com/n/ryqq/playlist/8212965281'}}))
drain(9)
js = """(function(){var b=document.querySelector('.mod_btn_green'); if(b){b.click(); return 'clicked';} return 'none';})()"""
ws.send(json.dumps({'id': 4, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'returnByValue': True}}))
drain(9)
ws.close()

for rid, r in list(seen.items())[:6]:
    print('URL:', r['url'])
    if r.get('postData'):
        try:
            d = json.loads(r['postData'])
            print('POST:', json.dumps(d, ensure_ascii=False)[:1500])
        except Exception:
            print('POST raw:', r['postData'][:800])
    print('-' * 60)
