# MT25040
# PA02: Analysis of Network I/O Primitives using "perf" Tool

## Student Information
- **Roll Number:** MT25040
- **Course:** Graduate Systems (CSE638)
- **Assignment:** PA02 - Network I/O Performance Analysis
- **Deadline:** February 7, 2026

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Implementation Details](#implementation-details)
3. [System Requirements](#system-requirements)
4. [File Structure](#file-structure)
5. [Compilation Instructions](#compilation-instructions)
6. [Execution Instructions](#execution-instructions)
7. [Experimental Setup](#experimental-setup)
8. [Results and Analysis](#results-and-analysis)
9. [AI Usage Declaration](#ai-usage-declaration)

---

## Project Overview

This assignment experimentally studies the cost of data movement in network I/O by implementing and comparing three different socket communication approaches:

1. **A1 - Two-Copy (Baseline):** Standard `send()`/`recv()` implementation
2. **A2 - One-Copy:** Optimized using `writev()` with scatter-gather I/O
3. **A3 - Zero-Copy:** Advanced implementation using `sendmsg()` with `MSG_ZEROCOPY` flag

### Objectives
- Measure throughput, latency, CPU cycles, and cache behavior
- Compare performance across different message sizes and thread counts
- Analyze micro-architectural effects of different I/O strategies
- Understand kernel behavior and data movement costs

---

## Implementation Details

### Part A1: Two-Copy Implementation (Baseline)
**Files:** `MT25040_Part_A1_Client.c`, `MT25040_Part_A1_Server.c`

**Key Features:**
- Uses standard `send()` and `recv()` system calls
- Server creates a message structure with 8 dynamically allocated fields
- Flattens the message into a single buffer using `memcpy()`
- Each client thread receives messages in a loop

**Data Movement:**
1. **First Copy:** User space (flat_buffer) → Kernel space (socket send buffer)
2. **Second Copy:** Kernel space (socket receive buffer) → User space (client buffer)

### Part A2: One-Copy Implementation
**Files:** `MT25040_Part_A2_Server.c`

**Key Features:**
- Uses `writev()` for scatter-gather I/O
- Eliminates the flattening step - sends directly from 8 separate buffers
- Constructs `iovec` array pointing to message fields
- Kernel gathers data from multiple user-space buffers

**Optimization:**
- **Eliminated Copy:** The `memcpy()` operation that flattened the message structure
- Data is sent directly from original buffers without intermediate copying

### Part A3: Zero-Copy Implementation
**Files:** `MT25040_Part_A3_Server.c`

**Key Features:**
- Uses `sendmsg()` with `MSG_ZEROCOPY` flag
- Enables `SO_ZEROCOPY` socket option
- Kernel uses DMA to transfer data directly from user buffers to NIC
- Includes retry logic for `ENOBUFS` errors

**Kernel Behavior:**
- User-space buffers are pinned in memory
- Network hardware accesses buffers via DMA
- Kernel notifies application when buffers can be reused
- Eliminates copy to kernel socket buffer

### Common Components
**Files:** `MT25040_Part_A_Data.h`

**Configuration:**
- `PORT`: 8080
- `ITERATIONS`: 1000 (configurable for testing)
- Message structure with 8 fields
- Helper functions: `generate_msg()`, `free_msg()`

---

## System Requirements

### Hardware
- Multi-core CPU (tested on 4 vCPU system)
- Sufficient RAM for concurrent threads
- Network interface supporting zerocopy (for A3)

### Software
- **OS:** Ubuntu 22.04 LTS (or compatible Linux distribution)
- **Kernel:** 4.14+ (for MSG_ZEROCOPY support)
- **Compiler:** GCC with pthread support
- **Tools:**
  - `perf` (Linux performance analysis tool)
  - `python3` with `matplotlib`
  - `ip` command (iproute2 package)
  - `bash` (version 4.0+)

### Required Packages
```bash
sudo apt-get update
sudo apt-get install build-essential linux-tools-common linux-tools-generic \
                     python3 python3-matplotlib iproute2
```

---

## File Structure

```
MT25040_PA02/
│
├── Makefile                              # Build configuration
├── README.md                             # This file
│
├── MT25040_Part_A1_Client.c             # Client implementation (all versions)
├── MT25040_Part_A1_Server.c             # Two-copy server
├── MT25040_Part_A2_Server.c             # One-copy server
├── MT25040_Part_A3_Server.c             # Zero-copy server
├── MT25040_Part_A_Data.h                # Common data structures and constants
│
├── MT25040_Part_C_Script.sh             # Automated experiment runner
├── MT25040_Part_D_Plots.py              # Visualization script
│
│
└── MT25040_PA02_Report.pdf              # Comprehensive analysis report
```

---

## Compilation Instructions

### Using Makefile

The project includes a comprehensive Makefile for easy compilation:

```bash
# Clean previous builds
make clean

# Compile all implementations
make

# Or compile individually
make server_a1
make server_a2
make server_a3
make client_a1
```

### Manual Compilation

If needed, you can compile manually:

```bash
# A1 Server (Two-Copy)
gcc -o server_a1 MT25040_Part_A1_Server.c -pthread -O2

# A2 Server (One-Copy)
gcc -o server_a2 MT25040_Part_A2_Server.c -pthread -O2

# A3 Server (Zero-Copy)
gcc -o server_a3 MT25040_Part_A3_Server.c -pthread -O2

# Client (shared for all)
gcc -o client_a1 MT25040_Part_A1_Client.c -pthread -O2
```

---

## Execution Instructions

### Automated Execution (Recommended)

The assignment includes a comprehensive bash script that automates the entire experimental workflow:

```bash
# Make script executable
chmod +x MT25040_Part_C_Script.sh

# Run all experiments
sudo ./MT25040_Part_C_Script.sh
```

**What the script does:**
1. Creates network namespaces (`ns_server`, `ns_client`)
2. Sets up virtual ethernet pairs
3. Compiles all implementations
4. Runs experiments across all combinations:
   - Message sizes: 1024, 16384, 65536, 262144 bytes
   - Thread counts: 1, 2, 4, 8
   - Implementations: A1, A2, A3
5. Collects `perf` metrics (cycles, context switches, cache misses)
6. Saves results to `final_results.csv`
7. Cleans up network namespaces

### Manual Execution

For testing individual configurations:

#### Step 1: Setup Network Namespaces
```bash
# Create namespaces
sudo ip netns add ns_server
sudo ip netns add ns_client

# Create virtual ethernet pair
sudo ip link add veth_server type veth peer name veth_client

# Move interfaces to namespaces
sudo ip link set veth_server netns ns_server
sudo ip link set veth_client netns ns_client

# Configure IP addresses
sudo ip netns exec ns_server ip addr add 10.0.0.1/24 dev veth_server
sudo ip netns exec ns_server ip link set veth_server up
sudo ip netns exec ns_server ip link set lo up

sudo ip netns exec ns_client ip addr add 10.0.0.2/24 dev veth_client
sudo ip netns exec ns_client ip link set veth_client up
sudo ip netns exec ns_client ip link set lo up
```

#### Step 2: Run Server
```bash
# Example: Run A1 server with 1024 byte messages
sudo ip netns exec ns_server ./server_a1 1024
```

#### Step 3: Run Client with Perf
```bash
# Get server PID
SERVER_PID=$(pidof server_a1)

# Run client with performance monitoring
sudo perf stat -p $SERVER_PID \
    -e cycles,context-switches,cache-misses,L1-dcache-load-misses \
    ip netns exec ns_client ./client_a1 10.0.0.1 8080 4 1024
```

#### Step 4: Cleanup
```bash
sudo killall -9 server_a1 server_a2 server_a3 client_a1
sudo ip netns del ns_server
sudo ip netns del ns_client
```

---

## Experimental Setup

### Test Parameters

| Parameter | Values |
|-----------|--------|
| **Message Sizes** | 1024, 16384, 65536, 262144 bytes |
| **Thread Counts** | 1, 2, 4, 8 |
| **Iterations** | 1000 per experiment |
| **Implementations** | A1 (Baseline), A2 (One-Copy), A3 (Zero-Copy) |

### Metrics Collected

1. **Throughput (Gbps):** Total data transferred per second
2. **Latency (μs):** Average time per message
3. **CPU Cycles:** Total cycles consumed
4. **Context Switches:** Number of thread context switches
5. **LLC Misses:** Last Level Cache misses
6. **L1 Misses:** L1 Data cache load misses

### Network Configuration

- **Topology:** Network namespaces with veth pairs
- **Server IP:** 10.0.0.1
- **Client IP:** 10.0.0.2
- **Port:** 8080
- **Protocol:** TCP

---

## Results and Analysis

### Visualization

Generate plots from experimental data:

```bash
python3 MT25040_Part_D_Plots.py
```

**Generated Plots:**
1. `1_throughput_analysis.png` - Throughput vs Message Size (4 subplots for each thread count)
2. `2_latency_analysis.png` - Latency vs Thread Count (4 subplots for each message size)
3. `3_cache_misses_analysis.png` - LLC Misses vs Message Size
4. `4_cpu_efficiency_analysis.png` - CPU Cycles/Byte vs Message Size

### Key Findings

**Throughput Trends:**
- All implementations show improved throughput with larger message sizes
- Zero-copy (A3) achieves highest throughput at large message sizes and high thread counts
- Performance gap widens significantly beyond 64KB messages

**Latency Observations:**
- Latency decreases with increasing thread count (better parallelization)
- A2 and A3 show competitive latency at optimal configurations
- Some anomalies at 8 threads due to contention

**Cache Behavior:**
- LLC misses increase significantly with message size
- A3 shows higher cache misses due to buffer pinning and DMA overhead
- A1 and A2 have similar cache patterns for small messages

**CPU Efficiency:**
- Cycles/byte decreases dramatically with larger messages (amortization of overhead)
- A3 becomes most efficient at 256KB messages
- All implementations converge in efficiency at very large message sizes

---

## Contact Information

For questions or clarifications regarding this assignment:
- **Student:** MT25040
- **Course:** CSE638 - Graduate Systems
- **Institution:** [University Name]

---

## License

This project is submitted as part of academic coursework. All rights reserved.

---

## Acknowledgments

- Course Instructor and TAs for assignment guidelines
- Linux kernel documentation for zero-copy mechanisms