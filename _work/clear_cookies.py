# -*- coding: utf-8 -*-
"""清空 CDP 浏览器 Cookie 并重新加载 y.qq.com，强制重新登录。"""
import json, time, requests, websocket

t = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type') == 'page'][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=40, suppress_origin=True)
ws.send(json.dumps({'id': 1, 'method': 'Network.enable'}))
ws.send(json.dumps({'id': 2, 'method': 'Network.clearBrowserCookies'}))
time.sleep(2)
ws.send(json.dumps({'id': 3, 'method': 'Page.navigate', 'params': {'url': 'https://y.qq.com/'}}))
time.sleep(6)
ws.close()
print('cleared+reloaded')
