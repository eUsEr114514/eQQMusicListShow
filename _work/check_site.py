# -*- coding: utf-8 -*-
"""用无头 Chrome 验证页面：点击首曲，检查 audio 元数据与错误。"""
import json, subprocess, time, sys
import requests, websocket

CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
URL = 'file:///E:/Code/DSH/MaybePurge/DownloadSongs/114514Songs/index.html'
PORT = 9444

p = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--mute-audio',
                      '--remote-debugging-port=%d' % PORT,
                      '--user-data-dir=E:/Code/DSH/MaybePurge/DownloadSongs/_work/hl-profile',
                      '--window-size=1440,1000', URL],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            tg = requests.get('http://127.0.0.1:%d/json' % PORT, timeout=2).json()
            break
        except Exception:
            time.sleep(0.5)
    page = [t for t in tg if t.get('type') == 'page'][0]
    ws = websocket.create_connection(page['webSocketDebuggerUrl'], timeout=30, suppress_origin=True)
    ws.settimeout(2)

    def ev(expr, await_promise=False):
        ws.send(json.dumps({'id': 9, 'method': 'Runtime.evaluate',
                            'params': {'expression': expr, 'awaitPromise': await_promise, 'returnByValue': True}}))
        while True:
            m = json.loads(ws.recv())
            if m.get('id') == 9:
                r = m.get('result', {}).get('result', {})
                return r.get('value'), m.get('result', {}).get('exceptionDetails')

    time.sleep(3)
    print('cards:', ev("document.querySelectorAll('.card').length")[0])
    print('imgs loaded:', ev("Array.from(document.images).filter(i=>i.complete&&i.naturalWidth>0).length")[0])
    ev("document.querySelector('.card').click()")
    time.sleep(4)
    print('src:', ev("document.querySelector('audio')? 'no-audio-el' : (window.__a ? '' : '')")[0])
    print('state:', ev("(()=>{const a=document.querySelector('audio');return a?JSON.stringify({src:a.src.slice(-60),rs:a.readyState,dur:a.duration,err:a.error&&a.error.code}):'no audio tag'})()")[0])
    print('title:', ev("document.querySelector('#ptitle').textContent")[0])
    ws.close()
finally:
    p.terminate()
