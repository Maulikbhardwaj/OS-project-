


from memory.models import Process
from memory.allocator import Memory
from sysinfo.system_mem import snapshot, pretty_print


def run_scenario(method: str) -> Memory:
    
    print(f"\n== {method.upper()}-FIT example ==")

    
    mem = Memory(total=300, initial_free_sizes=[90, 60, 50, 100])

    
    A = Process("A", 70)
    B = Process("B", 40)
    C = Process("C", 80)
    D = Process("D", 60)

    
    for p in (A, B, C, D):
        ok = mem.allocate(p, method=method)
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

    return mem


def print_comparison(mem: Memory) -> None:
    
    print("\nTaking system memory snapshot...")

    snap = snapshot()

   
    sim = mem.stats()
    free_blocks = [b for b in mem.blocks if b.free]
    num_holes = len(free_blocks)

    print("\n=== Simulator vs System ===")
    print(f"Simulator total units: {sim['sim_total']}")
    print(f"Simulator used units : {sim['sim_used']}")
    print(f"Simulator free units : {sim['sim_free']}")
    print(f"Largest free hole    : {sim['sim_largest_hole']}")
    print(f"External frag (est.) : {sim['sim_ext_frag_ratio']*100:.1f}%")
    print(f"Number of holes      : {num_holes}")
    print(f"Compaction bytes moved (total): {mem.compaction_cost()}")

    
    print("\nSystem snapshot:")
    pretty_print(snap)


if __name__ == "__main__":
    
    methods = ["first", "best", "worst", "next"]
    last_mem = None

    for m in methods:
        last_mem = run_scenario(m)

    if last_mem is not None:
        print_comparison(last_mem)
