# -*- coding: utf-8 -*-
"""在 y.qq.com 页面上下文里执行 JS（利用真实浏览器会话）。"""
import json, sys, requests, websocket

CDP = 'http://127.0.0.1:9333'


def page_ws(match='y.qq.com'):
    targets = requests.get(CDP + '/json', timeout=10).json()
    pages = [t for t in targets if t.get('type') == 'page']
    for t in pages:
        if match in t.get('url', ''):
            return t
    return pages[0]


def evaluate(expr, ws_url=None, timeout=60):
    t = page_ws()
    ws = websocket.create_connection((ws_url or t['webSocketDebuggerUrl']), timeout=timeout, suppress_origin=True)
    try:
        ws.send(json.dumps({'id': 1, 'method': 'Runtime.enable'}))
        ws.recv()
        ws.send(json.dumps({'id': 2, 'method': 'Runtime.evaluate', 'params': {
            'expression': expr, 'awaitPromise': True, 'returnByValue': True}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get('id') == 2:
                return msg
    finally:
        ws.close()


if __name__ == '__main__':
    expr = sys.stdin.read()
    r = evaluate(expr)
    print(json.dumps(r, ensure_ascii=False)[:4000])
