

from typing import List, Dict, Any
from typing import Callable, Tuple, List
# ---- Fault curve + Belady scan utilities ----

from typing import Callable, Tuple, List

AlgoFn = Callable[[List[int], int], dict]  # expects {"faults": int, ...}

def faults_vs_frames(ref: List[int], algo_fn: AlgoFn, min_f: int = 1, max_f: int = 10) -> List[Tuple[int, int]]:
    """
    Returns a list of (frames, faults) for frames=min_f..max_f using algo_fn(ref, frames).
    """
    curve = []
    for f in range(min_f, max_f + 1):
        res = algo_fn(ref, f)
        curve.append((f, res["faults"]))
    return curve

def belady_points(curve: List[Tuple[int, int]]) -> List[Tuple[int, int, int, int]]:
    """
    Given a curve [(frames,faults),...], return any (f_prev, faults_prev, f, faults)
    where faults increased when frames increased (Belady's anomaly).
    """
    bad = []
    for i in range(1, len(curve)):
        (f_prev, fp), (f, fc) = curve[i - 1], curve[i]
        if fc > fp:
            bad.append((f_prev, fp, f, fc))
    return bad

def print_curve(title: str, curve: List[Tuple[int, int]]):
    print(title)
    print("frames : faults")
    for f, faults in curve:
        print(f"{f:>6} : {faults}")


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
def simulate_clock(ref, frames_count):
    # Second-Chance (Clock): approximate LRU with one ref bit per frame.
    frames = []           # holds page numbers
    refbit = []           # parallel array of reference bits
    hand = 0              # clock hand index
    history, faults = [], 0

    def find(page):
        try: return frames.index(page)
        except ValueError: return -1

    for p in ref:
        idx = find(p)
        if idx != -1:
            # hit: set ref bit
            refbit[idx] = 1
            history.append((p, frames.copy(), "HIT"))
            continue

        faults += 1
        if len(frames) < frames_count:
            frames.append(p)
            refbit.append(1)
        else:
            # advance hand until we find a frame with refbit=0
            while True:
                if refbit[hand] == 0:
                    # evict here
                    frames[hand] = p
                    refbit[hand] = 1
                    hand = (hand + 1) % frames_count
                    break
                else:
                    # give second chance
                    refbit[hand] = 0
                    hand = (hand + 1) % frames_count
        history.append((p, frames.copy(), "FAULT"))
    return {"faults": faults, "history": history}


if __name__ == "__main__":
    REF = [7,0,1,2,0,3,0,4,2]
    for name, fn in [("FIFO", simulate_fifo), ("LRU", simulate_lru), ("Optimal", simulate_optimal),("CLOCK", simulate_clock)]:
        res = fn(REF, frames_count=3)
        print(f"\n{name} with 3 frames")
        print("ref | frames              | result")
        for r, fr, resu in res["history"]:
            print(f"{r:>3} | {str(fr):<20} | {resu}")
        print("faults:", res["faults"], "/", len(REF))
    print("\n== Fault curves (1..7 frames) ==")
    algos = [
        ("FIFO", simulate_fifo),
        ("LRU", simulate_lru),
        ("Optimal", simulate_optimal),
        # Uncomment if you added it:
        # ("CLOCK", simulate_clock),
    ]

    for name, fn in algos:
        curve = faults_vs_frames(REF, fn, min_f=1, max_f=7)
        print_curve(f"{name} curve", curve)
        bad = belady_points(curve)
        if bad:
            print(f"  Belady anomaly points for {name}:")
            for f_prev, fp, f, fc in bad:
                print(f"    frames {f_prev}->{f}: faults {fp}->{fc}  (INCREASE)")
        else:
            print(f"  No Belady anomaly detected for {name}.")
        print()
