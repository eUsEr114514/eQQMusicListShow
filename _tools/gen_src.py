# -*- coding: utf-8 -*-
"""把 Release 直链写入 data/tracks.js 的每一首（字段 src）。

用法：python _tools/gen_src.py
读取：_work/release_assets.json（资源名 -> 直链）
"""
import json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
DATA = os.path.join(BASE, '114514Songs', 'data', 'tracks.js')
ASSETS = os.path.join(WORK, 'release_assets.json')


def load_data():
    raw = open(DATA, encoding='utf-8').read()
    start = raw.index('{')
    end = raw.rindex('}')
    return raw[:start], raw[end + 1:], json.loads(raw[start:end + 1])


def main():
    prefix, suffix, data = load_data()
    if not os.path.exists(ASSETS):
        print('no assets json')
        return 1
    assets = json.load(open(ASSETS, encoding='utf-8'))
    by_n = {}
    for name, url in assets.items():
        m = re.match(r'^(\d+)-', name)
        if m:
            by_n[int(m.group(1))] = url

    hit, miss = 0, []
    for t in data['tracks']:
        url = by_n.get(t['n'])
        if url:
            t['src'] = url
            hit += 1
        else:
            t.pop('src', None)
            miss.append(t['n'])

    out = prefix + json.dumps(data, ensure_ascii=False, indent=1) + suffix
    open(DATA, 'w', encoding='utf-8').write(out)
    print('tracks', len(data['tracks']), 'with src', hit, 'missing', len(miss))
    if miss:
        print('missing n:', miss[:30])
    return 0


if __name__ == '__main__':
    sys.exit(main())
