# -*- coding: utf-8 -*-
"""真实鼠标点击播放按钮，抓取页面 vkey 请求/响应全文。"""
import json, time, requests, websocket

t = [x for x in requests.get('http://127.0.0.1:9333/json', timeout=10).json() if x.get('type') == 'page'][0]
ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=120, suppress_origin=True)
ws.settimeout(2)
ws.send(json.dumps({'id': 1, 'method': 'Network.enable', 'params': {'maxPostDataSize': 200000}}))
ws.send(json.dumps({'id': 2, 'method': 'Page.enable'}))

reqs, bodies = {}, {}
mid_id = [100]


def send(method, params):
    mid_id[0] += 1
    ws.send(json.dumps({'id': mid_id[0], 'method': method, 'params': params}))
    return mid_id[0]


def drain(sec):
    end = time.time() + sec
    while time.time() < end:
        try:
            m = json.loads(ws.recv())
        except Exception:
            continue
        meth = m.get('method')
        if meth == 'Network.requestWillBeSent':
            p = m['params']
            if 'musicu.fcg' in p['request']['url']:
                reqs[p['requestId']] = p['request']
        elif meth == 'Network.loadingFinished':
            rid = m['params']['requestId']
            if rid in reqs:
                i = send('Network.getResponseBody', {'requestId': rid})
                bodies[i] = rid
        elif 'id' in m and m['id'] in bodies:
            rid = bodies.pop(m['id'])
            r = m.get('result', {})
            print('=== ', reqs[rid]['url'][:100])
            print('REQ:', (reqs[rid].get('postData') or '')[:600])
            print('RESP:', (r.get('body') or '')[:600])


drain(1)
send('Page.navigate', {'url': 'https://y.qq.com/n/ryqq/songDetail/004XzGsM308yjw'})
drain(8)
js = """(function(){
  var b=[...document.querySelectorAll('a,button,div,span,i')].filter(function(e){
     var c=(e.className||'').toString();
     return /play/i.test(c) && e.getBoundingClientRect().width>10 && e.getBoundingClientRect().width<200;
  });
  if(!b.length) return 'none';
  var r=b[0].getBoundingClientRect();
  return JSON.stringify({x:r.x+r.width/2,y:r.y+r.height/2,cls:b[0].className});
})()"""
i = send('Runtime.evaluate', {'expression': js, 'returnByValue': True})
pos = None
end = time.time() + 5
while time.time() < end:
    try:
        m = json.loads(ws.recv())
    except Exception:
        continue
    if m.get('id') == i:
        v = m['result']['result'].get('value')
        print('btn:', v)
        if v and v != 'none':
            pos = json.loads(v)
        break

if pos:
    send('Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': pos['x'], 'y': pos['y'], 'button': 'left', 'clickCount': 1})
    send('Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': pos['x'], 'y': pos['y'], 'button': 'left', 'clickCount': 1})
drain(12)
ws.close()
