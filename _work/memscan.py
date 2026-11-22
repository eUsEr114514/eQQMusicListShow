# -*- coding: utf-8 -*-
"""扫描 QQMusic 客户端进程内存，提取登录相关 token（qm_keyst / qqmusic_key / uin）。"""
import ctypes, re, sys, time
from ctypes import wintypes

k32 = ctypes.WinDLL('kernel32', use_last_error=True)
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [('BaseAddress', ctypes.c_void_p), ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', wintypes.DWORD), ('RegionSize', ctypes.c_size_t),
                ('State', wintypes.DWORD), ('Protect', wintypes.DWORD), ('Type', wintypes.DWORD)]


k32.OpenProcess.restype = wintypes.HANDLE
k32.VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

PAGE_GUARD = 0x100
READABLE = (0x02, 0x04, 0x20, 0x40, 0x80)


def regions(h):
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    limit = 0x7FFFFFFF0000
    while addr < limit:
        if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.State == 0x1000 and mbi.Protect & 0xFF in READABLE and not (mbi.Protect & PAGE_GUARD):
            yield mbi.BaseAddress, mbi.RegionSize
        addr += mbi.RegionSize or 0x1000


PATTERNS = [b'qm_keyst=', b'qqmusic_key=', b'qm_keyst"', 'qm_keyst'.encode('utf-16-le'),
            'qqmusic_key'.encode('utf-16-le')]


def scan(pid, max_mb=3000):
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        print('open fail', ctypes.get_last_error())
        return []
    found = []
    total = 0
    buf = ctypes.create_string_buffer(1 << 20)
    read = ctypes.c_size_t(0)
    try:
        for base, size in regions(h):
            off = 0
            while off < size:
                n = min(1 << 20, size - off)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(base + off), buf, n, ctypes.byref(read)):
                    data = buf.raw[:read.value]
                    for pat in PATTERNS:
                        i = data.find(pat)
                        while i != -1:
                            found.append((base + off + i, pat, data[max(0, i - 80):i + 220]))
                            i = data.find(pat, i + 1)
                off += n
                total += n
                if total > max_mb * (1 << 20):
                    return found
    finally:
        k32.CloseHandle(h)
    return found


def show(hits):
    seen = set()
    for addr, pat, ctx in hits:
        try:
            txt = ctx.decode('utf-8', 'ignore')
        except Exception:
            continue
        for m in re.finditer(r'(qm_keyst|qqmusic_key)\s*[=:]\s*([A-Za-z0-9_\-]{40,200})', txt):
            key = m.group(2)
            if key not in seen:
                seen.add(key)
                print('FOUND', m.group(1), '=', key[:20] + '...' + key[-6:], 'len', len(key))
    if not seen:
        for addr, pat, ctx in hits[:5]:
            print(hex(addr), pat[:20], ctx[:160])


if __name__ == '__main__':
    pid = int(sys.argv[1])
    t = time.time()
    hits = scan(pid)
    print('hits', len(hits), 'in %.1fs' % (time.time() - t))
    show(hits)
