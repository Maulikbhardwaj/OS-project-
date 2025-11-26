# Operating Systems & Networking Simulator

This repository contains two core modules designed for Operating Systems and Networking coursework. It simulates core operating system concepts including memory management, paging algorithms, and network subnet calculations. This project demonstrates fundamental OS principles through practical implementations and visualizations.

## Table of Contents

- [Project Structure](#Project-Structure)
- [Features](#Features)
- [Project Structure](#Project-Structure)
- [Installation](#Installation)
- [Usage](#Usage)
  - [Memory Management](#Memory-Management)
  - [Paging Algorithms](#Paging-Algorithms)
  - [Network Subnet Calculator](#Network-Subnet-Calculator)
  - [System Information](#System-Information)
  - [Analysis Reports](#Analysis-Reports)
- [Modules Overview](#modules-overview)
- [Examples](#examples)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Project Structure
- **CPU Scheduling Simulator** - runs classical scheduling algorithms on real Linux process data.
- **Subnetting Calculator** - computes subnet masks, usable hosts, and address ranges automatically.
- **Cross-platform behaviour** - works on local machines and headless EC2 environments.
- **Clear, structured outputs** - includes tables, Gantt charts, and subnet summaries.


## Features

### Memory Management
- **Multiple allocation strategies**: First-Fit, Best-Fit, Worst-Fit, Next-Fit
- **Dynamic memory allocation and deallocation**
- **Memory compaction** with cost tracking
- **Fragmentation analysis** (external fragmentation metrics)
- **Visual memory representation** (ASCII and tabular views)

### Paging Algorithms
- **FIFO (First-In-First-Out)** page replacement
- **LRU (Least Recently Used)** page replacement
- **Optimal** page replacement (Belady's algorithm)
- **Clock** page replacement algorithm
- **Belady's anomaly detection**
- **Fault vs. frames curve analysis**

### Network Tools
- **Subnet calculator** with CIDR notation support
- **IP address classification** (Class A/B/C/D/E)
- **Binary representation** of IP addresses and masks
- **Subnet splitting** based on host requirements
- **Overlap detection** between network ranges
- **Wildcard mask calculation**
- **System IP detection** (Linux/macOS)

### System Information
- **Real-time memory snapshots** from the host system
- **Cross-platform support** (Linux and macOS)
- **Comparative analysis** between simulator and actual system memory

##  Project Structure

```

├── memory/
│   ├── __init__.py
│   ├── allocator.py          # Core memory allocation algorithms
│   ├── demo_memory.py         # Memory management demonstrations
│   ├── models.py              # Data models (Process, Block)
│   └── README.md
├── net/
│   ├── __init__.py
│   └── subnet_calc.py         # Subnet calculator and network utilities
├── paging/
│   ├── __init__.py
│   ├── algorithms.py          # Page replacement algorithms
│   ├── curves.py              # Fault analysis and curve generation
│   └── demo_paging.py         # Paging algorithm demonstrations
├── reports/
│   ├── __init__.py
│   └── analysis_report.py     # Visual analysis and reporting
└── sysinfo/
    ├── __init__.py
    └── system_mem.py          # System memory information utilities
```

##  Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Maulikbhardwaj/OS-project-.git
cd OS-project-
```

2. **Install dependencies**:
```bash
pip install matplotlib
```

3. **Verify installation**:
```bash
python -m memory.demo_memory
python -m paging.demo_paging
```

##  Usage

### Memory Management

Run the memory allocation simulator with different fitting strategies:

```bash
python -m memory.demo_memory
```

**Programmatic usage**:
```python
from memory.allocator import Memory
from memory.models import Process

# Initialize memory with 300 units
mem = Memory(total=300, initial_free_sizes=[90, 60, 50, 100])

# Create processes
process_a = Process("A", 70)
process_b = Process("B", 40)

# Allocate using different strategies
mem.allocate(process_a, method="first")  # First-Fit
mem.allocate(process_b, method="best")   # Best-Fit

# Display memory state
mem.print_table()
mem.print_ascii()

# Get statistics
stats = mem.stats()
print(f"External Fragmentation: {stats['sim_ext_frag_ratio']*100:.1f}%")

# Deallocate and compact
mem.deallocate("B")
mem.compact()
```

### Paging Algorithms

Run paging simulations and detect Belady's anomaly:

```bash
python -m paging.demo_paging
```

**Programmatic usage**:
```python
from paging.algorithms import simulate_fifo, simulate_lru, simulate_optimal
from paging.curves import faults_vs_frames, belady_points

# Define page reference string
ref_string = [7, 0, 1, 2, 0, 3, 0, 4, 2]

# Simulate FIFO with 3 frames
result = simulate_fifo(ref_string, frames_count=3)
print(f"Page faults: {result['faults']}")

# Generate fault vs. frames curve
curve = faults_vs_frames(ref_string, simulate_fifo, min_f=1, max_f=7)

# Detect Belady's anomaly
anomalies = belady_points(curve)
if anomalies:
    print("Belady's anomaly detected!")
```

### Network Subnet Calculator

**Command-line interface**:

```bash
# Basic subnet information
python -m net.subnet_calc 192.168.1.0/24

# Split network for specific host requirements
python -m net.subnet_calc 10.0.0.0/16 --hosts 50

# Check overlap between two networks
python -m net.subnet_calc --overlap 192.168.1.0/24 192.168.2.0/24

# Get system IP address
python -m net.subnet_calc --system-ip

# JSON output
python -m net.subnet_calc 172.16.0.0/12 --json

# Run examples
python -m net.subnet_calc --examples
```

**Programmatic usage**:
```python
from net.subnet_calc import info, split_for_hosts, overlap

# Get subnet information
subnet_info = info("192.168.1.0/24")
print(f"Network: {subnet_info['network']}")
print(f"Usable hosts: {subnet_info['hosts_usable']}")
print(f"Broadcast: {subnet_info['broadcast']}")

# Split network for host requirements
subnets = split_for_hosts("10.0.0.0/16", hosts_per_subnet=100)
for subnet in subnets:
    print(subnet)

# Check if two networks overlap
is_overlapping = overlap("192.168.1.0/24", "192.168.1.128/25")
```

### System Information

Get real-time system memory information:

```bash
python -m sysinfo.system_mem
```

**Programmatic usage**:
```python
from sysinfo.system_mem import snapshot, pretty_print

# Get system memory snapshot
mem_snapshot = snapshot()
pretty_print(mem_snapshot)
```

### Analysis Reports

Generate visual reports comparing memory fragmentation and page fault curves:

```bash
python -m reports.analysis_report
```

This generates:
- External fragmentation over memory operations (matplotlib plot)
- Page fault curves for FIFO, LRU, and Optimal algorithms (matplotlib plot)

##  Modules Overview

### `memory/`
- **`allocator.py`**: Implements memory allocation algorithms (First-Fit, Best-Fit, Worst-Fit, Next-Fit) with compaction and coalescing support
- **`models.py`**: Defines `Process` and `Block` data structures
- **`demo_memory.py`**: Demonstrates memory allocation scenarios and compares with system memory

### `paging/`
- **`algorithms.py`**: Implements FIFO, LRU, Optimal, and Clock page replacement algorithms
- **`curves.py`**: Generates fault vs. frames curves and detects Belady's anomaly
- **`demo_paging.py`**: Runs demonstrations of all paging algorithms with step-by-step traces

### `net/`
- **`subnet_calc.py`**: Comprehensive subnet calculator with CIDR support, subnet splitting, overlap detection, and IP classification

### `sysinfo/`
- **`system_mem.py`**: Cross-platform system memory information retrieval (supports Linux and macOS)

### `reports/`
- **`analysis_report.py`**: Generates visual analysis reports using matplotlib for memory and paging metrics

##  Examples

### Memory Allocation Example Output

```
== FIRST-FIT example ==
Alloc A(70) -> True
Alloc B(40) -> True
Alloc C(80) -> True
Alloc D(60) -> True
Start  End    Size   State   Tag
    0     70     70  USED   A
   70    110     40  USED   B
  110    170     60  FREE   -
  170    250     80  USED   C
  250    300     50  FREE   -

[0]###############--------###############-----[300]  (#=used, -=free)

=== Simulator vs System ===
Simulator total units: 300
Simulator used units : 190
Simulator free units : 110
Largest free hole    : 60
External frag (est.) : 45.5%
Number of holes      : 2
```

### Paging Algorithm Example Output

```
FIFO with 3 frames
ref | frames              | result
  7 | [7]                 | FAULT
  0 | [7, 0]              | FAULT
  1 | [7, 0, 1]           | FAULT
  2 | [2, 0, 1]           | FAULT
  0 | [2, 0, 1]           | HIT
  3 | [2, 3, 1]           | FAULT
  0 | [2, 3, 0]           | FAULT
  4 | [4, 3, 0]           | FAULT
  2 | [4, 2, 0]           | FAULT
faults: 8 / 9
```

### Subnet Calculator Example Output

```
------------------------------------------------------------
Subnet information for 192.168.1.0/24
------------------------------------------------------------
Network:       192.168.1.0/24
Mask:          255.255.255.0
Wildcard:      0.0.0.255
Broadcast:     192.168.1.255
Usable range:  192.168.1.1 → 192.168.1.254
Usable hosts:  254 (total: 256)
Block size:    256
Class:         C
Private network: Yes
Global routable: No

Binary representations:
Network:       11000000.10101000.00000001.00000000
Mask:          11111111.11111111.11111111.00000000
Broadcast:     11000000.10101000.00000001.11111111
Wildcard:      00000000.00000000.00000000.11111111
```

##  Requirements

- **Python 3.7+**
- **matplotlib** (for visual reports)
- **Linux or macOS** (for system memory information features)

##  Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

##  License

This project is part of an academic assignment and is provided for educational purposes.

##  Academic Context

This project demonstrates understanding of:
- Memory management techniques and allocation strategies
- Virtual memory and paging algorithms
- External fragmentation and compaction
- Network addressing and subnetting
- System-level programming and cross-platform compatibility

---

**Note**: This simulator is designed for educational purposes to understand operating system concepts. It is not intended for production use.
