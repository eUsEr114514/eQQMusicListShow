# -*- coding: utf-8 -*-
"""在 CDP 页面里导航并等待，用于触发站点自身的登录态刷新。"""
import json, sys, time, requests, websocket

url = sys.argv[1] if len(sys.argv) > 1 else 'https://y.qq.com/n/ryqq/profile'
wait = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0

t = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json()
     if x.get('type') == 'page' and 'y.qq.com' in x.get('url', '')]
t = t[0] if t else [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type') == 'page'][0]

ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=30, suppress_origin=True)
ws.send(json.dumps({'id': 1, 'method': 'Page.enable'}))
ws.send(json.dumps({'id': 2, 'method': 'Page.navigate', 'params': {'url': url}}))
time.sleep(wait)
ws.send(json.dumps({'id': 3, 'method': 'Runtime.evaluate', 'params': {
    'expression': 'document.title + " | " + location.href', 'returnByValue': True}}))
while True:
    m = json.loads(ws.recv())
    if m.get('id') == 3:
        print(json.dumps(m.get('result', {}), ensure_ascii=False)[:500])
        break
ws.close()
