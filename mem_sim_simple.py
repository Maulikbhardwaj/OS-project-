# mem_sim_simple.py
# A tiny, beginner-friendly memory allocator simulator:
# - Process class (instances = your jobs)
# - Blocks list to represent memory
# - First-Fit / Best-Fit / Worst-Fit / Next-Fit as separate methods
# - Deallocate + coalesce + (optional) compact
# - Simple print helpers

from dataclasses import dataclass
from typing import List, Optional
from system_mem import snapshot


# ---------- Models ----------
@dataclass
class Process:
    name: str
    size: int


@dataclass
class Block:
    start: int
    size: int
    free: bool = True
    tag: Optional[str] = None  # which process occupies it, if any

    @property
    def end(self) -> int:
        return self.start + self.size  # [start, end)


# ---------- Memory ----------
class Memory:
    def __init__(self, total: int, initial_free_sizes: Optional[List[int]] = None):
        self.total = total
        self.blocks: List[Block] = []
        self._next_fit_index = 0  # where Next-Fit will resume scanning

        if initial_free_sizes:
            pos = 0
            for sz in initial_free_sizes:
                self.blocks.append(Block(start=pos, size=sz, free=True))
                pos += sz
            if pos < total:
                self.blocks.append(Block(start=pos, size=total - pos, free=True))
        else:
            self.blocks = [Block(start=0, size=total, free=True)]

    # ---- Helpers ----
    def _coalesce(self) -> None:
        """Merge adjacent free blocks so they become one bigger free hole."""
        self.blocks.sort(key=lambda b: b.start)
        merged: List[Block] = []
        for b in self.blocks:
            if not merged:
                merged.append(b)
                continue
            last = merged[-1]
            if last.free and b.free and last.end == b.start:
                last.size += b.size
            else:
                merged.append(b)
        self.blocks = merged

    def compact(self) -> None:
        """Slide all used blocks to the left; create one free block at the end."""
        cur = 0
        new_blocks: List[Block] = []
        for b in sorted(self.blocks, key=lambda x: x.start):
            if not b.free:
                new_blocks.append(Block(start=cur, size=b.size, free=False, tag=b.tag))
                cur += b.size
        if cur < self.total:
            new_blocks.append(Block(start=cur, size=self.total - cur, free=True))
        self.blocks = new_blocks
        self._next_fit_index = 0

    # ---- Strategies ----
    def _find_first_fit(self, need: int) -> Optional[int]:
        for i, b in enumerate(self.blocks):
            if b.free and b.size >= need:
                return i
        return None

    def _find_best_fit(self, need: int) -> Optional[int]:
        candidates = [(i, b.size - need) for i, b in enumerate(self.blocks) if b.free and b.size >= need]
        if not candidates:
            return None
        return min(candidates, key=lambda x: x[1])[0]

    def _find_worst_fit(self, need: int) -> Optional[int]:
        candidates = [(i, b.size - need) for i, b in enumerate(self.blocks) if b.free and b.size >= need]
        if not candidates:
            return None
        return max(candidates, key=lambda x: x[1])[0]

    def _find_next_fit(self, need: int) -> Optional[int]:
        n = len(self.blocks)
        for off in range(n):
            i = (self._next_fit_index + off) % n
            b = self.blocks[i]
            if b.free and b.size >= need:
                self._next_fit_index = i  # next scan resumes here
                return i
        return None

    # ---- Public API ----
    def allocate(self, process: Process, method: str) -> bool:
        """Place `process` using a strategy: 'first', 'best', 'worst', 'next'."""
        method = method.lower()
        if method == "first":
            idx = self._find_first_fit(process.size)
        elif method == "best":
            idx = self._find_best_fit(process.size)
        elif method == "worst":
            idx = self._find_worst_fit(process.size)
        elif method == "next":
            idx = self._find_next_fit(process.size)
        else:
            raise ValueError("method must be one of: first, best, worst, next")

        if idx is None:
            return False  # no hole big enough

        hole = self.blocks[idx]
        if hole.size == process.size:
            hole.free = False
            hole.tag = process.name
        else:
            used = Block(start=hole.start, size=process.size, free=False, tag=process.name)
            rest = Block(start=hole.start + process.size, size=hole.size - process.size, free=True)
            self.blocks[idx] = used
            self.blocks.insert(idx + 1, rest)
        return True

    def deallocate(self, tag: str) -> bool:
        changed = False
        for b in self.blocks:
            if not b.free and b.tag == tag:
                b.free = True
                b.tag = None
                changed = True
        if changed:
            self._coalesce()
        return changed

    # ---- Printing ----
    def print_table(self) -> None:
        print("Start  End    Size   State   Tag")
        for b in sorted(self.blocks, key=lambda x: x.start):
            state = "FREE" if b.free else "USED"
            print(f"{b.start:>5}  {b.end:>5}  {b.size:>5}  {state:<6} {b.tag or '-'}")

    def print_ascii(self, width: int = 60) -> None:
        segs = []
        for b in sorted(self.blocks, key=lambda x: x.start):
            w = max(1, int(width * b.size / self.total))
            segs.append(("#" if not b.free else "-") * w)
        print(f"[0]{''.join(segs)}[{self.total}]  (#=used, -=free)")
def summarize_sim(mem) -> dict:
    total = mem.total
    free_blocks = [b for b in mem.blocks if b.free]
    used_blocks = [b for b in mem.blocks if not b.free]
    free_total = sum(b.size for b in free_blocks)
    used_total = sum(b.size for b in used_blocks)
    largest_hole = max((b.size for b in free_blocks), default=0)
    ext_frag = 0.0 if free_total == 0 else (free_total - largest_hole) / free_total
    return {
        "sim_total": total,
        "sim_used": used_total,
        "sim_free": free_total,
        "sim_largest_hole": largest_hole,
        "sim_ext_frag_ratio": round(ext_frag, 3),
    }

def print_comparison(mem, sys_snap: dict):
    sim = summarize_sim(mem)
    print("\n=== Simulator vs System ===")
    print(f"Simulator total units: {sim['sim_total']}")
    print(f"Simulator used units : {sim['sim_used']}")
    print(f"Simulator free units : {sim['sim_free']}")
    print(f"Largest free hole    : {sim['sim_largest_hole']}")
    print(f"External frag (est.) : {sim['sim_ext_frag_ratio']*100:.1f}%")
    from system_mem import pretty_print
    print("\nSystem snapshot:")
    pretty_print(sys_snap)


# ---------- Minimal demo ----------
if __name__ == "__main__":
    # Example memory: total 300, free blocks laid out as 90 | 60 | 50 | 100
    mem = Memory(total=300, initial_free_sizes=[90, 60, 50, 100])

    # Create some processes
    A = Process("A", 70)
    B = Process("B", 40)
    C = Process("C", 80)
    D = Process("D", 60)

    print("\n== FIRST-FIT example ==")
    for p in (A, B, C, D):
        ok = mem.allocate(p, method="first")
        print(f"Alloc {p.name}({p.size}) -> {ok}")
    mem.print_table()
    mem.print_ascii()

    print("\nDeallocate B then compact ...")
    mem.deallocate("B")
    mem.print_table()
    mem.print_ascii()
    mem.compact()
    mem.print_table()
    mem.print_ascii()
    print("\nTaking system memory snapshot...")
    
    snap = snapshot()
    print_comparison(mem, snap)


