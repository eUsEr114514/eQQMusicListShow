# -*- coding: utf-8 -*-
"""从 CDP 端点抓取 y.qq.com 登录 Cookie。"""
import json, sys, requests, websocket

CDP = 'http://127.0.0.1:9333'


def page_ws():
    targets = requests.get(CDP + '/json', timeout=10).json()
    pages = [t for t in targets if t.get('type') == 'page']
    for t in pages:
        if 'y.qq.com' in t.get('url', ''):
            return t
    return pages[0] if pages else None


def cdp_call(ws_url, method, params=None, _id=1):
    ws = websocket.create_connection(ws_url, timeout=20, suppress_origin=True)
    try:
        ws.send(json.dumps({'id': 1, 'method': 'Network.enable'}))
        ws.recv()
        ws.send(json.dumps({'id': 2, 'method': method, 'params': params or {}}))
        while True:
            msg = json.loads(ws.recv())
            if msg.get('id') == 2:
                return msg
    finally:
        ws.close()


def main():
    t = page_ws()
    print('page:', t.get('url') if t else None)
    resp = cdp_call(t['webSocketDebuggerUrl'], 'Network.getAllCookies')
    cookies = resp['result']['cookies']
    mine = [c for c in cookies if 'qq.com' in c['domain']]
    print('qq.com cookies:', len(mine))
    for c in mine:
        print(' %-22s %-22s len=%d' % (c['name'], c['domain'], len(c['value'])))
    json.dump(cookies, open('DownloadSongs/_work/cookies.json', 'w'), ensure_ascii=False)

    jar = {c['name']: c['value'] for c in mine}
    uin = jar.get('uin') or jar.get('p_uin') or ''
    print('uin raw:', uin)
    print('has qm_keyst:', bool(jar.get('qm_keyst')), 'has qqmusic_key:', bool(jar.get('qqmusic_key')),
          'has p_skey:', bool(jar.get('p_skey')), 'wxuin:', bool(jar.get('wxuin')))


if __name__ == '__main__':
    main()
