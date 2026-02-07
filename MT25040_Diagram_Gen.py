import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_zerocopy_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # ==========================================
    # 1. DEFINE ZONES (User, Kernel, Hardware)
    # ==========================================
    # User Space
    ax.add_patch(patches.Rectangle((0, 6), 10, 3, linewidth=2, edgecolor='black', facecolor='#E3F2FD'))
    ax.text(0.2, 8.5, "USER SPACE", fontsize=12, fontweight='bold', color='#1565C0')
    
    # Kernel Space
    ax.add_patch(patches.Rectangle((0, 3), 10, 3, linewidth=2, edgecolor='black', facecolor='#FFF3E0'))
    ax.text(0.2, 5.5, "KERNEL SPACE", fontsize=12, fontweight='bold', color='#E65100')
    
    # Hardware
    ax.add_patch(patches.Rectangle((0, 0), 10, 3, linewidth=2, edgecolor='black', facecolor='#E8F5E9'))
    ax.text(0.2, 2.5, "HARDWARE", fontsize=12, fontweight='bold', color='#2E7D32')

    # ==========================================
    # 2. DRAW COMPONENTS
    # ==========================================
    # Application Buffer (The Data)
    ax.add_patch(patches.Rectangle((1, 6.5), 3, 1.5, linewidth=2, edgecolor='#1565C0', facecolor='#BBDEFB'))
    ax.text(2.5, 7.25, "Application\nBuffer\n(Data)", fontsize=10, ha='center', va='center', fontweight='bold')

    # Socket Buffer (The Bypass Target)
    ax.add_patch(patches.Rectangle((1, 3.5), 3, 1.5, linewidth=2, edgecolor='#E65100', facecolor='#FFE0B2', linestyle='--'))
    ax.text(2.5, 4.25, "Socket Buffer\n(SKB)", fontsize=10, ha='center', va='center', color='#E65100')
    
    # NIC (Network Interface Card)
    ax.add_patch(patches.Rectangle((6, 0.5), 3, 1.5, linewidth=2, edgecolor='#2E7D32', facecolor='#C8E6C9'))
    ax.text(7.5, 1.25, "NIC / DMA\nController", fontsize=10, ha='center', va='center', fontweight='bold')

    # ==========================================
    # 3. DRAW ARROWS (The Data Flow)
    # ==========================================
    
    # A. The Traditional Copy (Crossed Out)
    # Arrow from App to Kernel
    ax.annotate("", xy=(2.5, 5), xytext=(2.5, 6.5),
                arrowprops=dict(arrowstyle="->", color="red", lw=2, linestyle="dashed"))
    # Cross out the copy
    ax.text(2.6, 5.8, "CPU Copy\n(Avoided)", fontsize=9, color='red', fontweight='bold')
    ax.text(2.5, 5.8, "X", fontsize=20, color='red', ha='center', va='center', fontweight='bold')

    # B. The Zero-Copy Path (Direct DMA)
    # We draw a curved arrow from App Buffer directly to NIC
    # ConnectionStyle="arc3,rad=-0.3" creates a nice curve
    ax.annotate("", xy=(6, 1.25), xytext=(4, 6.5),
                arrowprops=dict(arrowstyle="->", color="green", lw=4, 
                                connectionstyle="arc3,rad=-0.2"))
    
    # Label the Zero-Copy Path
    ax.text(5.5, 4.5, "DMA Transfer\n(Direct Memory Access)", fontsize=11, 
            fontweight='bold', color='green', bbox=dict(facecolor='white', edgecolor='green'))

    # ==========================================
    # 4. MEMORY PINNING VISUAL
    # ==========================================
    # Draw a "Pin" connecting User Buffer to Page Table
    ax.add_patch(patches.Circle((4, 6.5), 0.1, color='black'))
    ax.text(4.2, 6.6, "Pages Pinned\n(Locked in RAM)", fontsize=9, fontstyle='italic')

    # ==========================================
    # 5. CLEANUP
    # ==========================================
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9)
    ax.axis('off')
    plt.title("Zero-Copy Data Path (MSG_ZEROCOPY)", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('zerocopy_diagram.png', dpi=300)
    print("Success: Generated 'zerocopy_diagram.png'")

if __name__ == "__main__":
    draw_zerocopy_diagram()