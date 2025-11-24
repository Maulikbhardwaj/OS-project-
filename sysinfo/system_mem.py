import platform
import re
import subprocess


def _run(cmd: str) -> str:
    out = subprocess.check_output(cmd, shell=True, text=True)
    return out.strip()


def _linux_meminfo() -> dict:
    text = _run("cat /proc/meminfo")
    kv = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        kv[k.strip()] = v.strip()

    def to_mb(s: str):
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
        "source": "/proc/meminfo",
    }


def _macos_vm_stat() -> dict:
    text = _run("vm_stat")

    m = re.search(r"page size of\s+(\d+)\s+bytes", text)
    page_size = int(m.group(1)) if m else 4096

    pages = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = int(re.sub(r"[^\d]", "", v)) if re.search(r"\d", v) else 0
            pages[k] = v

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
        "available_mb": None,
        "buffers_mb": None,
        "cached_mb": None,
        "source": "vm_stat",
    }


def _macos_detailed_snapshot() -> None:
    """Print raw vm_stat/top/sysctl output for the report."""
    print("\n[macOS DETAILED SNAPSHOT]")
    print("==> vm_stat:")
    print(_run("vm_stat"))

    print("\n==> top -l 1 | grep PhysMem:")
    print(_run("top -l 1 | grep PhysMem"))

    print("\n==> sysctl hw.memsize:")
    print(_run("sysctl hw.memsize"))


def snapshot() -> dict:
    sys = platform.system().lower()
    try:
        if "linux" in sys:
            return _linux_meminfo()
        if "darwin" in sys:
            _macos_detailed_snapshot()
            return _macos_vm_stat()
    except Exception as e:
        return {"error": str(e)}
    return {"error": f"unsupported platform: {sys}"}


def pretty_print(snap: dict) -> None:
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
        print(f"  Cached:     {snap['cached_mb']}")


if __name__ == "__main__":
    snap = snapshot()
    pretty_print(snap)
