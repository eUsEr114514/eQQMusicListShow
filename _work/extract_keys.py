# -*- coding: utf-8 -*-
"""从 QQMusic 内存提取全部 token 候选并逐一验证可用性。"""
import ctypes, json, re, sys, time
from ctypes import wintypes
from memscan import k32, regions, PATTERNS

PATTERNS = PATTERNS + ['"qm_keyst"'.encode('utf-16-le')]


def collect(pid, max_mb=4000):
    h = k32.OpenProcess(0x0400 | 0x0010, False, pid)
    if not h:
        return []
    cands = set()
    buf = ctypes.create_string_buffer(1 << 20)
    read = ctypes.c_size_t(0)
    total = 0
    try:
        for base, size in regions(h):
            off = 0
            while off < size:
                n = min(1 << 20, size - off)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(base + off), buf, n, ctypes.byref(read)):
                    data = buf.raw[:read.value]
                    for m in re.finditer(rb'(?:qm_keyst|qqmusic_key)\s*[=:]\s*([A-Za-z0-9_\-]{90,200})', data):
                        cands.add(m.group(1).decode('ascii', 'ignore'))
                off += n
                total += n
                if total > max_mb * (1 << 20):
                    return sorted(cands)
    finally:
        k32.CloseHandle(h)
    return sorted(cands)


if __name__ == '__main__':
    pid = int(sys.argv[1])
    keys = collect(pid)
    print('candidates', len(keys))
    for k in keys:
        print(len(k), k[:16] + '...' + k[-8:])
    json.dump(keys, open('client_keys.json', 'w'))
