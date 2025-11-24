from paging.algorithms import (
    simulate_fifo,
    simulate_lru,
    simulate_optimal,
    simulate_clock,
)
from paging.curves import faults_vs_frames, belady_points, print_curve


REF = [7, 0, 1, 2, 0, 3, 0, 4, 2]


def run_step_traces() -> None:
    for name, fn in [
        ("FIFO", simulate_fifo),
        ("LRU", simulate_lru),
        ("Optimal", simulate_optimal),
        ("CLOCK", simulate_clock),
    ]:
        res = fn(REF, frames_count=3)
        print(f"\n{name} with 3 frames")
        print("ref | frames              | result")
        for r, fr, resu in res["history"]:
            print(f"{r:>3} | {str(fr):<20} | {resu}")
        print("faults:", res["faults"], "/", len(REF))


def run_fault_curves() -> None:
    print("\n== Fault curves (1..7 frames) ==")
    algos = [
        ("FIFO", simulate_fifo),
        ("LRU", simulate_lru),
        ("Optimal", simulate_optimal),
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


if __name__ == "__main__":
    run_step_traces()
    run_fault_curves()
