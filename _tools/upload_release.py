# -*- coding: utf-8 -*-
"""把 SongsFiles 里的音频以 ASCII 名上传到 GitHub Release。

用法：
  python _tools/upload_release.py --repo eUsEr114514/eQQMusicListShow --tag songs-v1 --token <PAT>

命名：{序号}-{英文转写}.{扩展名}，例如 3-Yu_Lu_Shuang_Xue.flac
产出：_work/release_assets.json （序号 -> 资源名 / 直链）
"""
import argparse, json, os, re, sys, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

import requests
from unidecode import unidecode

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(BASE, '_work')
FILES = os.path.join(BASE, '114514Songs', 'SongsFiles')
API = 'https://api.github.com'
UP = 'https://uploads.github.com'


def slugify(title, n):
    s = unidecode(title)
    s = re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')
    s = re.sub(r'_+', '_', s)
    if len(s) > 60:
        s = s[:60].rstrip('_')
    return s or 'track'


def build_plan():
    rows = json.load(open(os.path.join(WORK, 'manifest.json'), encoding='utf-8'))
    plan = []
    for r in rows:
        base = r['file']
        exts = [e for e in ('.mp3', '.flac', '.m4a') if os.path.exists(os.path.join(FILES, base + e))]
        if not exts:
            continue
        ext = exts[0]
        local = base + ext
        name = '%d-%s%s' % (r['n'], slugify(r['name'], r['n']), ext)
        plan.append({'n': r['n'], 'local': local, 'asset': name,
                     'size': os.path.getsize(os.path.join(FILES, local))})
    return plan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--token', required=True)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--limit', type=int, default=0, help='只传前 N 个，用于试跑')
    args = ap.parse_args()

    H = {'Authorization': 'Bearer ' + args.token, 'Accept': 'application/vnd.github+json',
         'X-GitHub-Api-Version': '2022-11-28'}

    rel = requests.get('%s/repos/%s/releases/tags/%s' % (API, args.repo, args.tag), headers=H, timeout=30)
    rel.raise_for_status()
    rel = rel.json()
    rel_id = rel['id']
    print('release', rel_id, rel['html_url'], flush=True)

    existing = {}
    page = 1
    while True:
        r = requests.get('%s/repos/%s/releases/%d/assets' % (API, args.repo, rel_id),
                         headers=H, params={'per_page': 100, 'page': page}, timeout=60)
        r.raise_for_status()
        items = r.json()
        if not items:
            break
        for a in items:
            existing[a['name']] = a['browser_download_url']
        page += 1
    print('existing assets', len(existing), flush=True)

    plan = build_plan()
    todo = [p for p in plan if p['asset'] not in existing]
    if args.limit:
        todo = todo[:args.limit]
    print('todo', len(todo), 'of', len(plan), flush=True)

    lock = threading.Lock()
    done = {'ok': 0, 'fail': 0}
    results = dict(existing)

    def upload(p):
        path = os.path.join(FILES, p['local'])
        url = '%s/repos/%s/releases/%d/assets?name=%s' % (UP, args.repo, rel_id, quote(p['asset']))
        for attempt in range(4):
            try:
                with open(path, 'rb') as f:
                    r = requests.post(url, headers={**H, 'Content-Type': 'application/octet-stream'},
                                      data=f, timeout=1800)
                if r.status_code in (200, 201):
                    return p, r.json()['browser_download_url']
                if r.status_code == 422 and 'already_exists' in r.text:
                    return p, None
                time.sleep(2 * (attempt + 1))
            except Exception:
                time.sleep(3 * (attempt + 1))
        return p, False

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(upload, p): p for p in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            p, url = fut.result()
            with lock:
                if url:
                    results[p['asset']] = url
                    done['ok'] += 1
                elif url is None:
                    done['ok'] += 1
                else:
                    done['fail'] += 1
                if i % 10 == 0 or i == len(todo):
                    el = time.time() - t0
                    print('progress %d/%d ok=%d fail=%d %.1f min' % (i, len(todo), done['ok'], done['fail'], el / 60),
                          flush=True)
                    json.dump(results, open(os.path.join(WORK, 'release_assets.json'), 'w'), ensure_ascii=False, indent=0)

    json.dump(results, open(os.path.join(WORK, 'release_assets.json'), 'w'), ensure_ascii=False, indent=0)
    print('DONE ok=%d fail=%d total_assets=%d' % (done['ok'], done['fail'], len(results)))


if __name__ == '__main__':
    main()
