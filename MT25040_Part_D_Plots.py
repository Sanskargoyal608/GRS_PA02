import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
SYSTEM_CONFIG = "System: 16 vCPU, Fixed Backlog"
ITERATIONS = 1000

# ==========================================
# HARDCODED DATA (FULL DATASET FOR ALL GRAPHS)
# ==========================================
sizes = [1024, 16384, 65536, 262144]
threads = [1, 2, 4, 8]

# --- THROUGHPUT (Gbps) ---
tp_data = {
    1: {
        'a1': [0.19, 5.09, 18.06, 21.87],
        'a2': [0.30, 4.88, 17.06, 35.54],
        'a3': [0.32, 4.68, 14.37, 30.87]
    },
    2: {
        'a1': [0.67, 10.22, 32.92, 35.34],
        'a2': [0.69, 8.84, 35.08, 45.22],
        'a3': [0.57, 8.75, 19.02, 56.81]
    },
    4: {
        'a1': [1.38, 19.30, 54.13, 59.17],
        'a2': [0.79, 18.93, 65.31, 48.56],
        'a3': [1.16, 17.98, 46.29, 57.37]
    },
    8: {
        'a1': [2.66, 22.40, 96.30, 61.22],
        'a2': [2.47, 32.46, 104.17, 53.34],
        'a3': [1.21, 30.28, 70.37, 54.07]
    }
}

# --- LATENCY (us) ---
lat_data = {
    1024: {
        'a1': [42.02, 12.06, 5.91, 3.07],
        'a2': [26.57, 11.83, 10.36, 3.30],
        'a3': [24.99, 14.32, 7.05, 6.76]
    },
    16384: {
        'a1': [25.74, 12.82, 6.78, 5.85],
        'a2': [26.83, 14.82, 6.92, 4.03],
        'a3': [27.97, 14.97, 7.28, 4.32]
    },
    65536: {
        'a1': [29.02, 15.92, 9.68, 5.44],
        'a2': [30.72, 14.94, 8.02, 5.03],
        'a3': [36.45, 27.55, 11.32, 7.45]
    },
    262144: {
        'a1': [95.84, 59.32, 35.43, 34.25],
        'a2': [58.99, 46.37, 43.18, 39.31],
        'a3': [67.92, 36.91, 36.55, 38.78]
    }
}

# --- LLC MISSES (Raw Count - All Threads) ---
llc_data = {
    1: {
        'a1': [82378, 386032, 970920, 2538692],
        'a2': [117422, 377525, 980784, 3556353],
        'a3': [142350, 391910, 1655819, 6970171]
    },
    2: {
        'a1': [179421, 696834, 1924662, 5515685],
        'a2': [197559, 715908, 1848736, 6353735],
        'a3': [381736, 868812, 3098450, 12747157]
    },
    4: {
        'a1': [361521, 1316159, 3598334, 10715723],
        'a2': [415278, 1380425, 3648373, 11153499],
        'a3': [782245, 1668163, 6648452, 14404180]
    },
    8: {
        'a1': [878549, 2311479, 7172318, 24770389],
        'a2': [909561, 2235728, 7503929, 23470600],
        'a3': [2272925, 4203586, 12388609, 17327901]
    }
}

# --- RAW CYCLES (For CPU Efficiency Calculation) ---
cycles_data = {
    1: {
        'a1': [24181322, 42153700, 55665619, 200473496],
        'a2': [27545335, 36679883, 60328528, 171972767],
        'a3': [33791102, 50248468, 91759740, 228117737]
    },
    2: {
        'a1': [51500527, 81288058, 130218853, 543307838],
        'a2': [56631678, 84612949, 115295377, 488447332],
        'a3': [78600670, 112431400, 180044373, 486739494]
    },
    4: {
        'a1': [97026245, 165282289, 300460108, 1791324827],
        'a2': [112666479, 163926629, 242861875, 1960114721],
        'a3': [151197932, 210989468, 450295956, 590454561]
    },
    8: {
        'a1': [245376743, 391260429, 769403615, 6634530146],
        'a2': [254136113, 380456909, 687663330, 7680936616],
        'a3': [366331813, 568779553, 1019027292, 1485509026]
    }
}

# --- CPU EFFICIENCY CALCULATION ---
def calculate_cpb(cycles_list, thread_count):
    cpb_list = []
    for c, s in zip(cycles_list, sizes):
        total_bytes = s * thread_count * ITERATIONS
        cpb_list.append(c / total_bytes)
    return cpb_list

# Pre-calculate CPB for all threads
cpb_data = {}
for t in threads:
    cpb_data[t] = {
        'a1': calculate_cpb(cycles_data[t]['a1'], t),
        'a2': calculate_cpb(cycles_data[t]['a2'], t),
        'a3': calculate_cpb(cycles_data[t]['a3'], t)
    }

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
# GENERATE 4 IMAGES (Each with 4 Subplots)
# ==========================================

# 1. THROUGHPUT (4 Subplots: 1T, 2T, 4T, 8T)
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

# 2. LATENCY (4 Subplots: 1K, 16K, 65K, 262K)
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'Latency vs Thread Count ({SYSTEM_CONFIG})', fontsize=14)
for i, s in enumerate(sizes):
    ax = axs[i//2, i%2]
    ax.plot(threads, lat_data[s]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(threads, lat_data[s]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(threads, lat_data[s]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Size: {s} Bytes', 'Threads', 'Latency (us)')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('2_latency_analysis.png')

# 3. LLC MISSES (4 Subplots: 1T, 2T, 4T, 8T)
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'LLC Misses vs Message Size ({SYSTEM_CONFIG})', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, llc_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, llc_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, llc_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'LLC Misses', logx=True, logy=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('3_cache_misses_analysis.png')

# 4. CPU EFFICIENCY (4 Subplots: 1T, 2T, 4T, 8T)
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'CPU Efficiency vs Message Size ({SYSTEM_CONFIG})', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, cpb_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, cpb_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, cpb_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size (Bytes)', 'Cycles Per Byte', logx=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('4_cpu_efficiency_analysis.png')

print("All 4 Analysis Images (4x4 subplots) Generated with YOUR full data.")