import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
SYSTEM_CONFIG = "System: 4 vCPU, Ubuntu 22.04 LTS"
ITERATIONS = 1000  # Used for Cycles/Byte calculation

# ==========================================
# HARDCODED DATA (From your latest CSV)
# ==========================================
# Implementations: a1 (Baseline), a2 (One-Copy), a3 (Zero-Copy)
# Sizes: 1024, 16384, 65536, 262144
# Threads: 1, 2, 4, 8

sizes = [1024, 16384, 65536, 262144]
threads = [1, 2, 4, 8]

# Data organized by [Thread Count Index][Implementation] -> Array of values for sizes
# T1 (Index 0), T2 (Index 1), T4 (Index 2), T8 (Index 3)

# --- THROUGHPUT (Gbps) ---
tp_data = {
    1: { # Threads
        'a1': [0.13, 1.91, 6.46, 10.28],
        'a2': [0.16, 2.63, 8.44, 11.08],
        'a3': [0.17, 2.34, 7.08, 13.96]
    },
    2: {
        'a1': [0.34, 4.77, 16.04, 19.57],
        'a2': [0.27, 4.71, 16.77, 20.93],
        'a3': [0.34, 3.27, 12.99, 27.05]
    },
    4: {
        'a1': [0.71, 8.55, 28.41, 32.66],
        'a2': [0.65, 10.01, 29.49, 38.85],
        'a3': [0.66, 7.82, 26.71, 50.86]
    },
    8: {
        'a1': [1.32, 16.61, 3.75, 51.01],
        'a2': [0.06, 14.79, 41.99, 51.40],
        'a3': [1.20, 0.94, 36.12, 78.40]
    }
}

# --- LATENCY (us) ---
# Organized by [Message Size Index][Implementation] -> Array of values for threads
# S1024 (Index 0), S16384 (1), S65536 (2), S262144 (3)
lat_data = {
    1024: {
        'a1': [62.57, 24.24, 11.51, 6.22],
        'a2': [50.81, 30.81, 12.56, 133.94],
        'a3': [48.37, 23.99, 12.33, 6.84]
    },
    16384: {
        'a1': [68.77, 27.48, 15.34, 7.89],
        'a2': [49.74, 27.81, 13.09, 8.86],
        'a3': [55.93, 40.04, 16.76, 139.63]
    },
    65536: {
        'a1': [81.17, 32.69, 18.46, 139.87],
        'a2': [62.15, 31.27, 17.78, 12.49],
        'a3': [74.04, 40.37, 19.63, 14.52]
    },
    262144: {
        'a1': [203.91, 107.15, 64.21, 41.11],
        'a2': [189.34, 100.22, 53.98, 40.80],
        'a3': [150.19, 77.53, 41.23, 26.75]
    }
}

# --- LLC MISSES ---
# Organized by Threads (like Throughput)
llc_data = {
    1: {
        'a1': [102708, 352224, 990954, 3063599],
        'a2': [104083, 357289, 1078827, 3050255],
        'a3': [140390, 378699, 1646348, 6810335]
    },
    2: {
        'a1': [198703, 724016, 2040485, 6717545],
        'a2': [178464, 724508, 2062220, 6287349],
        'a3': [263916, 802332, 3153718, 13019331]
    },
    4: {
        'a1': [348766, 1388185, 4048625, 12351710],
        'a2': [446288, 1310796, 3866667, 12672143],
        'a3': [500607, 1883686, 6214807, 24660621]
    },
    8: {
        'a1': [689819, 2409369, 8154289, 22932225],
        'a2': [858142, 2757072, 8239809, 24677230],
        'a3': [1569044, 4320658, 12317849, 44189336]
    }
}

# --- CYCLES PER BYTE ---
# Calculated from Raw Cycles in CSV
# Formula: Cycles / (Size * Threads * ITERATIONS)
# Using hardcoded cycle counts to derive this
cycles_raw = {
    1: { # Threads
        'a1': [26014896, 39582137, 64156955, 192775113],
        'a2': [33030240, 36906354, 60541305, 124841792],
        'a3': [33796769, 50460855, 90962146, 249524109]
    },
    2: {
        'a1': [48751448, 82912974, 132468767, 652749702],
        'a2': [54570409, 85758224, 121481646, 288057741],
        'a3': [68218790, 105014358, 195234529, 471046937]
    },
    4: {
        'a1': [107696451, 180752828, 294310693, 1109154113],
        'a2': [112531222, 158875017, 260647622, 957348440],
        'a3': [133228783, 245949803, 357962899, 923829231]
    },
    8: {
        'a1': [251971002, 364424668, 609678773, 3377742287],
        'a2': [251493435, 446461360, 687860786, 3666798786],
        'a3': [358624069, 553340088, 857228833, 1988567149]
    }
}

# Helper to calculate Cycles/Byte
def get_cpb(thread_count, impl):
    raw = cycles_raw[thread_count][impl]
    cpb = []
    for i, size in enumerate(sizes):
        total_bytes = size * thread_count * ITERATIONS
        cpb.append(raw[i] / total_bytes)
    return cpb

# ==========================================
# PLOTTING UTILS
# ==========================================
def style_plot(ax, title, xlabel, ylabel, logx=False, logy=False):
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    if logx: ax.set_xscale('log', base=2)
    if logy: ax.set_yscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(fontsize=8)

# ==========================================
# 1. THROUGHPUT vs MESSAGE SIZE (4 Subplots)
# ==========================================
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'Throughput vs Message Size ({SYSTEM_CONFIG})', fontsize=14)

for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, tp_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, tp_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, tp_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'Throughput (Gbps)', logx=True)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('1_throughput_analysis.png')
print("Generated 1_throughput_analysis.png")

# ==========================================
# 2. LATENCY vs THREAD COUNT (4 Subplots)
# ==========================================
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'Latency vs Thread Count ({SYSTEM_CONFIG})', fontsize=14)

for i, s in enumerate(sizes):
    ax = axs[i//2, i%2]
    ax.plot(threads, lat_data[s]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(threads, lat_data[s]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(threads, lat_data[s]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Message Size: {s}', 'Thread Count', 'Latency (us)')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('2_latency_analysis.png')
print("Generated 2_latency_analysis.png")

# ==========================================
# 3. LLC MISSES vs MESSAGE SIZE (4 Subplots)
# ==========================================
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'LLC Cache Misses vs Message Size ({SYSTEM_CONFIG})', fontsize=14)

for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, llc_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, llc_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, llc_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'LLC Misses', logx=True, logy=True)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('3_cache_misses_analysis.png')
print("Generated 3_cache_misses_analysis.png")

# ==========================================
# 4. CPU CYCLES/BYTE vs MESSAGE SIZE (4 Subplots)
# ==========================================
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'CPU Efficiency (Cycles/Byte) vs Message Size ({SYSTEM_CONFIG})', fontsize=14)

for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    # Calculate CPB dynamically
    cpb_a1 = get_cpb(t, 'a1')
    cpb_a2 = get_cpb(t, 'a2')
    cpb_a3 = get_cpb(t, 'a3')
    
    ax.plot(sizes, cpb_a1, 'o-', label='A1 (Baseline)')
    ax.plot(sizes, cpb_a2, 's-', label='A2 (One-Copy)')
    ax.plot(sizes, cpb_a3, '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'Cycles / Byte', logx=True)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('4_cpu_efficiency_analysis.png')
print("Generated 4_cpu_efficiency_analysis.png")