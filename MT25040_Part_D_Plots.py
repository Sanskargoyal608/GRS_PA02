import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
SYSTEM_CONFIG = "System: 16 vCPU, Fixed Duration (6s)"
DPI = 300

# ==========================================
# RAW DATA (Directly from your latest CSV)
# ==========================================
sizes = [1024, 16384, 65536, 262144]
threads = [1, 2, 4, 8]

# --- THROUGHPUT (Gbps) ---
tp_data = {
    1: {'a1': [1.66, 14.16, 37.94, 29.60],
        'a2': [1.51, 13.05, 35.26, 46.30],
        'a3': [0.97, 9.26, 24.04, 36.40]},
    2: {'a1': [3.45, 26.83, 72.58, 66.14],
        'a2': [2.92, 24.80, 69.50, 82.05],
        'a3': [1.88, 18.22, 46.37, 64.98]},
    4: {'a1': [6.16, 47.38, 123.53, 90.54],
        'a2': [5.30, 43.72, 117.98, 105.55],
        'a3': [3.24, 31.91, 80.07, 110.27]},
    8: {'a1': [8.72, 64.25, 152.11, 68.83],
        'a2': [7.50, 59.94, 152.03, 55.38],
        'a3': [4.27, 43.51, 103.05, 75.85]}
}

# --- LATENCY (Raw Inter-Arrival Time from CSV) ---
lat_data = {
    1024: {'a1': [4.93, 2.37, 1.32, 0.93],
           'a2': [5.41, 2.80, 1.54, 1.09],
           'a3': [8.40, 4.33, 2.52, 1.91]},
    16384: {'a1': [9.25, 4.88, 2.76, 2.03],
            'a2': [10.04, 5.28, 2.99, 2.18],
            'a3': [14.14, 7.19, 4.10, 3.01]},
    65536: {'a1': [13.81, 7.22, 4.24, 3.44],
            'a2': [14.86, 7.54, 4.44, 3.44],
            'a3': [21.80, 11.30, 6.54, 5.08]},
    262144: {'a1': [70.83, 31.70, 23.16, 30.46],
             'a2': [45.28, 25.55, 19.86, 37.86],
             'a3': [57.61, 32.27, 19.01, 27.64]}
}

# --- L1 MISSES ---
l1_data = {
    1: {'a1': [2.67e8, 9.16e8, 1.80e9, 1.32e9],
        'a2': [2.81e8, 8.57e8, 1.68e9, 2.09e9],
        'a3': [3.09e8, 6.43e8, 1.13e9, 1.53e9]},
    2: {'a1': [5.59e8, 1.73e9, 3.43e9, 2.96e9],
        'a2': [5.68e8, 1.63e9, 3.30e9, 3.70e9],
        'a3': [6.01e8, 1.27e9, 2.20e9, 2.56e9]},
    4: {'a1': [1.06e9, 3.13e9, 5.89e9, 4.00e9],
        'a2': [1.02e9, 2.93e9, 5.62e9, 4.69e9],
        'a3': [1.10e9, 2.25e9, 3.86e9, 4.13e9]},
    8: {'a1': [2.46e9, 4.90e9, 7.56e9, 3.11e9],
        'a2': [2.33e9, 4.55e9, 7.54e9, 2.49e9],
        'a3': [2.05e9, 3.63e9, 5.36e9, 1.73e9]}
}

# --- CPB CALCULATION (Formula: Cycles / Total_Bytes) ---
cycles_data = {
    1: {'a1': [2.28e10, 2.54e10, 2.50e10, 2.15e10],
        'a2': [2.44e10, 2.46e10, 2.43e10, 2.26e10],
        'a3': [2.33e10, 2.37e10, 2.39e10, 2.34e10]},
    2: {'a1': [5.01e10, 4.84e10, 4.76e10, 4.17e10],
        'a2': [4.74e10, 4.73e10, 4.66e10, 4.15e10],
        'a3': [4.56e10, 4.66e10, 4.65e10, 4.20e10]},
    4: {'a1': [9.13e10, 8.84e10, 8.69e10, 7.70e10],
        'a2': [8.66e10, 8.58e10, 8.49e10, 7.23e10],
        'a3': [8.31e10, 8.41e10, 8.41e10, 6.79e10]},
    8: {'a1': [1.64e11, 1.60e11, 1.57e11, 1.58e11],
        'a2': [1.56e11, 1.54e11, 1.51e11, 1.34e11],
        'a3': [1.39e11, 1.50e11, 1.48e11, 4.88e10]}
}

def calculate_cpb(cycles_list, throughput_list):
    cpb_list = []
    duration = 6.0
    for cycles, gbps in zip(cycles_list, throughput_list):
        if gbps > 0:
            total_bytes = (gbps * 1e9 * duration) / 8.0
            cpb_list.append(cycles / total_bytes)
        else:
            cpb_list.append(0)
    return cpb_list

cpb_data = {}
for t in threads:
    cpb_data[t] = {
        'a1': calculate_cpb(cycles_data[t]['a1'], tp_data[t]['a1']),
        'a2': calculate_cpb(cycles_data[t]['a2'], tp_data[t]['a2']),
        'a3': calculate_cpb(cycles_data[t]['a3'], tp_data[t]['a3'])
    }

# ==========================================
# PLOTTING FUNCTIONS
# ==========================================
def style_plot(ax, title, xlabel, ylabel, logx=False, logy=False):
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    if logx: ax.set_xscale('log', base=2)
    if logy: ax.set_yscale('log')
    ax.grid(True, which="both", ls="--", alpha=0.5)
    ax.legend(fontsize=8)

# 1. THROUGHPUT
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'Throughput vs Message Size ({SYSTEM_CONFIG})', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, tp_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, tp_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, tp_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'Throughput (Gbps)', logx=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('1_throughput_analysis.png', dpi=DPI)

# 2. LATENCY
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'System Latency (Inter-arrival) vs Thread Count', fontsize=14)
for i, s in enumerate(sizes):
    ax = axs[i//2, i%2]
    ax.plot(threads, lat_data[s]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(threads, lat_data[s]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(threads, lat_data[s]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Size: {s} Bytes', 'Threads', 'Latency (us)')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('2_latency_analysis.png', dpi=DPI)

# 3. L1 MISSES
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'L1 Cache Misses vs Message Size', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, l1_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, l1_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, l1_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'L1 Misses', logx=True, logy=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('3_cache_misses_analysis.png', dpi=DPI)

# 4. CPU CYCLES PER BYTE
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'CPU Cycles per Byte Transferred', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, cpb_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, cpb_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, cpb_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'CPU Cycles / Byte', logx=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('4_cpu_cycles_per_byte.png', dpi=DPI)

print("Success: Generated plain plots based on raw CSV.")