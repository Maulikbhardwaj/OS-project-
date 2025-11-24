import matplotlib.pyplot as plt

from memory.models import Process
from memory.allocator import Memory
from paging.algorithms import simulate_fifo, simulate_lru, simulate_optimal
from paging.curves import faults_vs_frames


def fragmentation_over_operations():
    mem = Memory(total=300, initial_free_sizes=[300])
    ops = []
    frags = []

    procs = [
        Process("A", 50),
        Process("B", 80),
        Process("C", 60),
        Process("D", 40),
    ]

    # sequence: alloc A,B,C, free B, alloc D, compact
    def record(step: str):
        stats = mem.stats()
        ops.append(step)
        frags.append(stats["sim_ext_frag_ratio"] * 100)

    record("start")
    for p in procs[:3]:
        mem.allocate(p, "first")
        record(f"alloc {p.name}")
    mem.deallocate("B")
    record("free B")
    mem.allocate(procs[3], "first")
    record("alloc D")
    mem.compact()
    record("compact")

    plt.figure()
    plt.plot(range(len(ops)), frags, marker="o")
    plt.xticks(range(len(ops)), ops, rotation=45)
    plt.ylabel("External fragmentation (%)")
    plt.title("External fragmentation vs operations")
    plt.tight_layout()
    plt.show()


def paging_fault_curve():
    ref = [7, 0, 1, 2, 0, 3, 0, 4, 2]
    frames = list(range(1, 8))

    fifo_curve = faults_vs_frames(ref, simulate_fifo, 1, 7)
    lru_curve = faults_vs_frames(ref, simulate_lru, 1, 7)
    opt_curve = faults_vs_frames(ref, simulate_optimal, 1, 7)

    plt.figure()
    plt.plot(frames, [f for _, f in fifo_curve], marker="o", label="FIFO")
    plt.plot(frames, [f for _, f in lru_curve], marker="o", label="LRU")
    plt.plot(frames, [f for _, f in opt_curve], marker="o", label="Optimal")
    plt.xlabel("Number of frames")
    plt.ylabel("Page faults")
    plt.title("Page-fault curves")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    fragmentation_over_operations()
    paging_fault_curve()
