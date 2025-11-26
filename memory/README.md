Our project demonstrates how operating systems allocate and manage memory using contiguous allocation strategies:
First fit, Worst fit, Best fit, Next fit, Compaction & External Fragmentation, Comparison with Real System Memory.

A brief into what is memory management: It ensures that processes get enough memory to run efficiently.
There 2 major techniques:
    a) Contiguous Allocation: A process must be placed in one continuous block of memory. This causes holes, fragmentation, and requires smart placement strategies.
    b) Fragmentation: Internal — wasted inside allocated block. External — many small holes that cannot fit a new process Compaction moves processes together to remove scattered free holes.


Allocation Algos usage:
a) First Fit: Picks the first hole large enough. It is fast but creates small leftover holes at the start
b) Best fit: Looks all holes and then picks the smallest in which the process can fit. It saves space but many tiny unusable holes are created.
c) Worst fit: Pick the largest free hole.They leave medium/large holes for future allocation but sometimes may waste space.
d) Next fit: Doesnt start from the beginning rather from the last allocation alloted. This approach though is more balanced but can skip good holes.


What our code does:
Let's start with models.py: This stores info about our each process and memory block. 
    @dataclass
    class Process:
        name: str
        size: int
This part of our code requests the memory to store its name and memory it needs.
    @dataclass
    class Block:
        start: int
         size: int
        free: bool = True
        tag: Optional[str] = None
This tells us where the block finishes(split,merged,free,used)
Start   End   Size   State   Tag
0       70     70    USED     A
This the output we could expect from running this file.



Coming to allocator.py: this implements the logic of allocation.
self.blocks = [Block(start=0, size=total, free=True)] # initialises the memory
This represents the intial memory layout and output is currently having free blocks.

_find_first_fit(), _find_best_fit(), _find_worst_fit(), _find_next_fit()
Then we allocate strategies to find which hole to allocate for which process.
Alloc A(70) -> True
Alloc D(60) -> False
A sample output of what we could expect.

hole = self.blocks[idx]
then we allocate split leftover space nd update the memory.
b.free = True
self._coalesce().  What this does it Shows holes after deallocation it reduces external fragmentation.

sim_used, sim_free, largest_hole, ext_frag_ratio
This part gives us the statistical analysis to compare allocation strategies and system memory

At the last we have demo_memory.py: Our main program which shows algo behaviour and system comparison.


Our is a simulator which models memory as continous blocks
	a)	Simulates
	b)	Allocating processes using First-Fit, Best-Fit, Worst-Fit, Next-Fit
	c)	Freeing memory and coalescing holes
	d)	Compaction to remove fragmentation
	e)	Provides ASCII visualization
    f) Tracks statistics like used/free memory, largest hole, external fragmentation.

Real Operating System Memory
	a) Uses paging and virtual memory, not contiguous blocks.
	b)	Manages memory with kernel allocators (buddy system, slab allocator).
	c)	Tracks: Total/used/free pages, Wired/active/compressed memory
	f)	Avoids external fragmentation in most cases.