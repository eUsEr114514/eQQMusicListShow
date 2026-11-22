import json, base64, requests, websocket
t = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type')=='page' and 'y.qq.com' in x['url']][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=30, suppress_origin=True)
ws.send(json.dumps({'id':1,'method':'Page.captureScreenshot','params':{'format':'png'}}))
while True:
    m = json.loads(ws.recv())
    if m.get('id')==1:
        open('DownloadSongs/_work/page.png','wb').write(base64.b64decode(m['result']['data']))
        print('saved')
        break
ws.close()
