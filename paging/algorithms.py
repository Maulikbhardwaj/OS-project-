from typing import List, Dict, Any


def simulate_fifo(ref: List[int], frames_count: int) -> Dict[str, Any]:
    frames: List[int] = []
    order: List[int] = []  # arrival order
    history, faults = [], 0

    for p in ref:
        if p in frames:
            history.append((p, frames.copy(), "HIT"))
            continue

        faults += 1
        if len(frames) < frames_count:
            frames.append(p)
            order.append(p)
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
            # farthest-in-future victim
            next_pos = {}
            for f in frames:
                try:
                    next_pos[f] = ref[i + 1 :].index(f)
                except ValueError:
                    next_pos[f] = float("inf")
            victim = max(frames, key=lambda x: next_pos[x])
            idx = frames.index(victim)
            frames[idx] = p

        history.append((p, frames.copy(), "FAULT"))

    return {"faults": faults, "history": history}


def simulate_clock(ref: List[int], frames_count: int) -> Dict[str, Any]:
    frames: List[int] = []
    refbit: List[int] = []
    hand = 0
    history, faults = [], 0

    def find(page: int) -> int:
        try:
            return frames.index(page)
        except ValueError:
            return -1

    for p in ref:
        idx = find(p)
        if idx != -1:
            refbit[idx] = 1
            history.append((p, frames.copy(), "HIT"))
            continue

        faults += 1
        if len(frames) < frames_count:
            frames.append(p)
            refbit.append(1)
        else:
            while True:
                if refbit[hand] == 0:
                    frames[hand] = p
                    refbit[hand] = 1
                    hand = (hand + 1) % frames_count
                    break
                else:
                    refbit[hand] = 0
                    hand = (hand + 1) % frames_count

        history.append((p, frames.copy(), "FAULT"))

    return {"faults": faults, "history": history}
