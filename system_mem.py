# system_mem.py
# Cross-platform memory snapshot for your report/demo.
# - Linux: parses /proc/meminfo (and optionally `free -m`)
# - macOS: parses `vm_stat` (pages) and converts to MB
# No external deps.

import platform
import re
import subprocess

def _run(cmd):
    out = subprocess.check_output(cmd, shell=True, text=True)
    return out.strip()

def _linux_meminfo():
    text = _run("cat /proc/meminfo")
    kv = {}
    for line in text.splitlines():
        if ":" not in line: 
            continue
        k, v = line.split(":", 1)
        kv[k.strip()] = v.strip()
    def to_mb(s):
        # e.g., "16312928 kB"
        m = re.search(r"([0-9]+)\s*kB", s)
        return int(m.group(1)) // 1024 if m else None
    total = to_mb(kv.get("MemTotal", ""))
    free = to_mb(kv.get("MemFree", ""))
    avail = to_mb(kv.get("MemAvailable", ""))  # better "free-ish"
    buffers = to_mb(kv.get("Buffers", "0 kB"))
    cached = to_mb(kv.get("Cached", "0 kB"))
    return {
        "os": "Linux",
        "total_mb": total,
        "free_mb": free,
        "available_mb": avail,
        "buffers_mb": buffers,
        "cached_mb": cached,
        "source": "/proc/meminfo"
    }

def _macos_vm_stat():
    # Example:
    # Mach Virtual Memory Statistics: (page size of 4096 bytes)
    # Pages free:                               12345.
    # Pages active:                             67890.
    # ...
    text = _run("vm_stat")
    # page size
    m = re.search(r"page size of\s+(\d+)\s+bytes", text)
    page_size = int(m.group(1)) if m else 4096
    pages = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = int(re.sub(r"[^\d]", "", v)) if re.search(r"\d", v) else 0
            pages[k] = v
    # Approximate totals (macOS doesn't expose MemAvailable directly)
    free_pages = pages.get("Pages free", 0) + pages.get("Pages speculative", 0)
    active = pages.get("Pages active", 0)
    inactive = pages.get("Pages inactive", 0)
    wired = pages.get("Pages wired down", 0) or pages.get("Pages wired", 0)

    total_pages = free_pages + active + inactive + wired
    to_mb = lambda p: (p * page_size) // (1024 * 1024)

    return {
        "os": "macOS",
        "total_mb": to_mb(total_pages),
        "free_mb": to_mb(free_pages),
        "available_mb": None,  # no clean analog via vm_stat
        "buffers_mb": None,
        "cached_mb": None,
        "source": "vm_stat"
    }

def snapshot():
    sys = platform.system().lower()
    try:
        if "linux" in sys:
            return _linux_meminfo()
        if "darwin" in sys:
            return _macos_vm_stat()
    except Exception as e:
        return {"error": str(e)}
    return {"error": f"unsupported platform: {sys}"}

def pretty_print(snap: dict):
    if "error" in snap:
        print("System memory snapshot error:", snap["error"])
        return
    print(f"[{snap['os']}] via {snap['source']}")
    print(f"  Total:      {snap['total_mb']} MB")
    print(f"  Free:       {snap['free_mb']} MB")
    if snap.get("available_mb") is not None:
        print(f"  Available:  {snap['available_mb']} MB")
    if snap.get("buffers_mb") is not None:
        print(f"  Buffers:    {snap['buffers_mb']} MB")
    if snap.get("cached_mb") is not None:
        print(f"  Cached:     {snap['cached_mb']} MB")


