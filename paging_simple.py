# paging_simple.py
# Minimal paging simulator with FIFO, LRU, Optimal on a reference string.

from typing import List, Dict, Any

def simulate_fifo(ref: List[int], frames_count: int) -> Dict[str, Any]:
    frames: List[int] = []
    order: List[int] = []
    history, faults = [], 0
    for p in ref:
        if p in frames:
            history.append((p, frames.copy(), "HIT"))
            continue
        faults += 1
        if len(frames) < frames_count:
            frames.append(p); order.append(p)
        else:
            victim = order.pop(0)
            idx = frames.index(victim)
            frames[idx] = p
            order.append(p)
        history.append((p, frames.copy(), "FAULT"))
    return {"faults": faults, "history": history}

def simulate_lru(ref: List[int], frames_count: int) -> Dict[str, Any]:
    frames: List[int] = []
    last_used: Dict[int, int] = {}
    history, faults = [], 0
    for t, p in enumerate(ref):
        if p in frames:
            last_used[p] = t
            history.append((p, frames.copy(), "HIT"))
            continue
        faults += 1
        if len(frames) < frames_count:
            frames.append(p)
        else:
            victim = min(frames, key=lambda x: last_used.get(x, -1))
            idx = frames.index(victim)
            frames[idx] = p
            last_used.pop(victim, None)
        last_used[p] = t
        history.append((p, frames.copy(), "FAULT"))
    return {"faults": faults, "history": history}

def simulate_optimal(ref: List[int], frames_count: int) -> Dict[str, Any]:
    frames: List[int] = []
    history, faults = [], 0
    n = len(ref)
    for i, p in enumerate(ref):
        if p in frames:
            history.append((p, frames.copy(), "HIT"))
            continue
        faults += 1
        if len(frames) < frames_count:
            frames.append(p)
        else:
            # choose the page used farthest in the future (or never again)
            next_pos = {}
            for f in frames:
                try:
                    next_pos[f] = ref[i+1:].index(f)
                except ValueError:
                    next_pos[f] = float("inf")
            victim = max(frames, key=lambda x: next_pos[x])
            idx = frames.index(victim)
            frames[idx] = p
        history.append((p, frames.copy(), "FAULT"))
    return {"faults": faults, "history": history}

if __name__ == "__main__":
    REF = [7,0,1,2,0,3,0,4,2]
    for name, fn in [("FIFO", simulate_fifo), ("LRU", simulate_lru), ("Optimal", simulate_optimal)]:
        res = fn(REF, frames_count=3)
        print(f"\n{name} with 3 frames")
        print("ref | frames              | result")
        for r, fr, resu in res["history"]:
            print(f"{r:>3} | {str(fr):<20} | {resu}")
        print("faults:", res["faults"], "/", len(REF))
