import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
SYSTEM_CONFIG = "System: 4 vCPU, Ubuntu 22.04 LTS"
ITERATIONS = 1000  # Used for Cycles/Byte calculation

# ==========================================
# HARDCODED DATA (From your Corrected A2 CSV)
# ==========================================
sizes = [1024, 16384, 65536, 262144]
threads = [1, 2, 4, 8]

# --- THROUGHPUT (Gbps) ---
tp_data = {
    1: {
        'a1': [0.21, 4.71, 16.94, 23.51],
        'a2': [0.35, 5.07, 17.23, 24.70],
        'a3': [0.34, 4.52, 13.41, 30.20] # A3 Wins at 262K (1 Thread)
    },
    2: {
        'a1': [0.76, 9.94, 33.08, 41.27],
        'a2': [0.70, 9.43, 30.45, 42.76],
        'a3': [0.52, 8.50, 26.76, 57.60] # A3 Wins Huge at 262K (2 Threads)
    },
    4: {
        'a1': [1.44, 19.11, 55.77, 62.85],
        'a2': [1.07, 19.62, 59.65, 73.02], # A2 Wins at 4 Threads
        'a3': [1.25, 17.67, 49.55, 68.13]
    },
    8: {
        'a1': [0.06, 0.99, 3.85, 14.54],
        'a2': [0.06, 0.98, 3.86, 15.29],
        'a3': [0.06, 1.00, 3.94, 14.90]
    }
}

# --- LATENCY (us) ---
lat_data = {
    1024: {
        'a1': [39.20, 10.79, 5.69, 130.40],
        'a2': [23.39, 11.72, 7.63, 133.62],
        'a3': [24.10, 15.66, 6.56, 134.25]
    },
    16384: {
        'a1': [27.80, 13.19, 6.86, 132.62],
        'a2': [25.84, 13.90, 6.68, 133.61],
        'a3': [28.97, 15.42, 7.42, 131.29]
    },
    65536: {
        'a1': [30.95, 15.85, 9.40, 136.26],
        'a2': [30.42, 17.22, 8.79, 135.85],
        'a3': [39.11, 19.59, 10.58, 133.20]
    },
    262144: {
        'a1': [89.22, 50.81, 33.37, 144.26],
        'a2': [84.90, 49.05, 28.72, 137.18],
        'a3': [69.45, 36.41, 30.78, 140.72]
    }
}

# --- LLC MISSES ---
llc_data = {
    1: {
        'a1': [110955, 338115, 936686, 2608263],
        'a2': [97889, 361914, 914522, 2453045],
        'a3': [140703, 411379, 1467410, 6974361]
    },
    2: {
        'a1': [167237, 672459, 1811047, 5423328],
        'a2': [184277, 668208, 1849900, 5234961],
        'a3': [305679, 792303, 3238020, 13521758]
    },
    4: {
        'a1': [363550, 1251704, 3665781, 11065096],
        'a2': [420949, 1291015, 3767159, 12066337],
        'a3': [654065, 1740185, 6789425, 14776614]
    },
    8: {
        'a1': [706874, 2621232, 7179774, 22167339],
        'a2': [864242, 2657295, 7283992, 23838955],
        'a3': [1388614, 3740147, 14890193, 47794441]
    }
}

# --- CYCLES PER BYTE (Efficiency) ---
# Derived from Cycles column in your CSV
cycles_raw = {
    1: {
        'a1': [25755341, 41914078, 63140335, 201708680],
        'a2': [26710240, 42837994, 62470701, 135644694],
        'a3': [33037015, 53298991, 102038865, 232133973]
    },
    2: {
        'a1': [49836103, 76370086, 128915491, 508144938],
        'a2': [53674589, 85511395, 137605613, 405228751],
        'a3': [81251025, 104825105, 190023761, 462479789]
    },
    4: {
        'a1': [106112583, 172570080, 303961445, 1485682365],
        'a2': [134681206, 174941434, 291559501, 1375434872],
        'a3': [144869306, 216696966, 410728150, 574356059]
    },
    8: {
        'a1': [239427519, 382379706, 595073956, 3976240956],
        'a2': [256950712, 402947686, 633370052, 5682966757],
        'a3': [338437201, 500327164, 896259447, 1932207687]
    }
}

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
# GENERATE 4 IMAGES
# ==========================================

# 1. THROUGHPUT
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'Throughput vs Message Size ({SYSTEM_CONFIG})', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, tp_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, tp_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, tp_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size', 'Throughput (Gbps)', logx=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('1_throughput_analysis.png')

# 2. LATENCY
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'Latency vs Thread Count ({SYSTEM_CONFIG})', fontsize=14)
for i, s in enumerate(sizes):
    ax = axs[i//2, i%2]
    ax.plot(threads, lat_data[s]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(threads, lat_data[s]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(threads, lat_data[s]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Size: {s}', 'Threads', 'Latency (us)')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('2_latency_analysis.png')

# 3. LLC MISSES
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'LLC Misses vs Message Size ({SYSTEM_CONFIG})', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    ax.plot(sizes, llc_data[t]['a1'], 'o-', label='A1 (Baseline)')
    ax.plot(sizes, llc_data[t]['a2'], 's-', label='A2 (One-Copy)')
    ax.plot(sizes, llc_data[t]['a3'], '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size', 'LLC Misses', logx=True, logy=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('3_cache_misses_analysis.png')

# 4. CPU EFFICIENCY
fig, axs = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle(f'CPU Efficiency vs Message Size ({SYSTEM_CONFIG})', fontsize=14)
for i, t in enumerate(threads):
    ax = axs[i//2, i%2]
    cpb_a1 = get_cpb(t, 'a1')
    cpb_a2 = get_cpb(t, 'a2')
    cpb_a3 = get_cpb(t, 'a3')
    ax.plot(sizes, cpb_a1, 'o-', label='A1 (Baseline)')
    ax.plot(sizes, cpb_a2, 's-', label='A2 (One-Copy)')
    ax.plot(sizes, cpb_a3, '^-', label='A3 (Zero-Copy)')
    style_plot(ax, f'Threads: {t}', 'Message Size', 'Cycles / Byte', logx=True)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('4_cpu_efficiency_analysis.png')

print("All 4 Analysis Images Generated.")