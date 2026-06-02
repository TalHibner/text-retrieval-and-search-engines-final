#!/usr/bin/env python3
"""
Analysis of ROBUST04 RRF Parameter Tuning Results
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Your tuning results
results_data = [
    {'k': 30, 'rerank_depth': 500, 'MAP': 0.2656, 'nDCG@10': 0.5011, 'time_s': 1037.6},
    {'k': 30, 'rerank_depth': 700, 'MAP': 0.2714, 'nDCG@10': 0.5021, 'time_s': 1429.1},
    {'k': 30, 'rerank_depth': 1000, 'MAP': 0.2728, 'nDCG@10': 0.5011, 'time_s': 2004.9},
    {'k': 40, 'rerank_depth': 500, 'MAP': 0.2645, 'nDCG@10': 0.5039, 'time_s': 1028.0},
    {'k': 40, 'rerank_depth': 700, 'MAP': 0.2702, 'nDCG@10': 0.5041, 'time_s': 1428.6},
    {'k': 40, 'rerank_depth': 1000, 'MAP': 0.2721, 'nDCG@10': 0.5057, 'time_s': 2005.5},
    {'k': 50, 'rerank_depth': 500, 'MAP': 0.2633, 'nDCG@10': 0.5024, 'time_s': 1028.6},
    {'k': 50, 'rerank_depth': 700, 'MAP': 0.2689, 'nDCG@10': 0.5025, 'time_s': 1428.2},
    {'k': 50, 'rerank_depth': 1000, 'MAP': 0.2706, 'nDCG@10': 0.5008, 'time_s': 2006.8},
    {'k': 60, 'rerank_depth': 500, 'MAP': 0.2627, 'nDCG@10': 0.5028, 'time_s': 1029.6},
]

df = pd.DataFrame(results_data)

# Sort by MAP
df_sorted = df.sort_values('MAP', ascending=False)

print("="*70)
print("📊 PARAMETER TUNING ANALYSIS")
print("="*70)
print("\n🏆 TOP 5 CONFIGURATIONS (by MAP):")
print("-"*70)
print(df_sorted.head(5).to_string(index=False))

print("\n\n" + "="*70)
print("🔍 KEY FINDINGS")
print("="*70)

# Best configuration
best = df_sorted.iloc[0]
print(f"\n1. BEST CONFIGURATION:")
print(f"   k = {int(best['k'])}")
print(f"   rerank_depth = {int(best['rerank_depth'])}")
print(f"   MAP = {best['MAP']:.4f}")
print(f"   nDCG@10 = {best['nDCG@10']:.4f}")
print(f"   Time = {best['time_s']:.1f}s")

# Compare to original
original_map = 0.2738
improvement = best['MAP'] - original_map
print(f"\n2. COMPARISON TO ORIGINAL WEIGHTED RRF:")
print(f"   Original MAP: {original_map:.4f}")
print(f"   Best Pure RRF MAP: {best['MAP']:.4f}")
print(f"   Change: {improvement:+.4f} ({improvement/original_map*100:+.2f}%)")

if improvement < 0:
    print(f"   ⚠️  Pure RRF performs WORSE than weighted RRF!")
    print(f"   🔍 This suggests weighted fusion was actually helping.")
else:
    print(f"   ✓ Pure RRF performs better!")

# Effect of k
print(f"\n3. EFFECT OF k VALUE:")
for k_val in sorted(df['k'].unique()):
    k_results = df[df['k'] == k_val]
    avg_map = k_results['MAP'].mean()
    print(f"   k={k_val}: Avg MAP = {avg_map:.4f}")

# Effect of rerank_depth
print(f"\n4. EFFECT OF RERANK_DEPTH:")
for depth in sorted(df['rerank_depth'].unique()):
    depth_results = df[df['rerank_depth'] == depth]
    avg_map = depth_results['MAP'].mean()
    avg_time = depth_results['time_s'].mean()
    print(f"   depth={depth}: Avg MAP = {avg_map:.4f}, Avg Time = {avg_time:.1f}s")

# Speed vs Performance tradeoff
print(f"\n5. SPEED vs PERFORMANCE TRADEOFF:")
fast_config = df.loc[df['time_s'].idxmin()]
best_config = df_sorted.iloc[0]
print(f"   Fastest: k={int(fast_config['k'])}, depth={int(fast_config['rerank_depth'])}")
print(f"            MAP={fast_config['MAP']:.4f}, Time={fast_config['time_s']:.1f}s")
print(f"   Best:    k={int(best_config['k'])}, depth={int(best_config['rerank_depth'])}")
print(f"            MAP={best_config['MAP']:.4f}, Time={best_config['time_s']:.1f}s")
time_increase = (best_config['time_s'] - fast_config['time_s']) / fast_config['time_s'] * 100
map_increase = (best_config['MAP'] - fast_config['MAP']) / fast_config['MAP'] * 100
print(f"   Tradeoff: +{time_increase:.1f}% time for +{map_increase:.2f}% MAP")

print("\n" + "="*70)
print("💡 RECOMMENDATIONS")
print("="*70)

if best['MAP'] < original_map:
    print("\n⚠️  IMPORTANT: Your original weighted RRF was actually BETTER!")
    print("\nRECOMMENDATION:")
    print("   Go back to weighted RRF with these improvements:")
    print("   • Keep weights: W_BM25=1.0, W_RM3=1.5, W_MONOT5=2.0")
    print(f"   • Use k={int(best['k'])} (best from tuning)")
    print(f"   • Use rerank_depth={int(best['rerank_depth'])} (best from tuning)")
    print("   • Keep improved RM3 parameters")
    print(f"\n   Expected MAP: ~{original_map:.4f} (original) or slightly better")
else:
    print(f"\n✓ Pure RRF is better! Use:")
    print(f"   • k = {int(best['k'])}")
    print(f"   • rerank_depth = {int(best['rerank_depth'])}")
    print(f"   Expected MAP: {best['MAP']:.4f}")

print("\n" + "="*70)
print("🎯 REACHING MAP 0.35")
print("="*70)
print(f"\nCurrent best: MAP = {best['MAP']:.4f}")
print(f"Target: MAP = 0.35")
print(f"Gap: {0.35 - best['MAP']:.4f} ({(0.35 - best['MAP'])/best['MAP']*100:.1f}% improvement needed)")

print("\nStrategies to close the gap:")
print("1. Add more retrieval signals:")
print("   • SPLADE (dense retrieval)")
print("   • ColBERTv2 (late interaction)")
print("   • Dense retrieval (ANCE, TCT-ColBERT)")
print("\n2. Better rerankers:")
print("   • MonoT5-3B (larger model)")
print("   • Cross-encoder (MiniLM-L12)")
print("   • Ensemble of rerankers")
print("\n3. Query processing:")
print("   • Query expansion beyond RM3")
print("   • Query classification (use different strategies per type)")
print("   • Multi-stage retrieval")
print("\n4. Document processing:")
print("   • Title/body field weighting")
print("   • Passage-level retrieval + aggregation")

print("\n" + "="*70)

# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: MAP vs k (by rerank_depth)
ax1 = axes[0, 0]
for depth in sorted(df['rerank_depth'].unique()):
    depth_data = df[df['rerank_depth'] == depth].sort_values('k')
    ax1.plot(depth_data['k'], depth_data['MAP'], marker='o', label=f'depth={depth}')
ax1.axhline(y=original_map, color='r', linestyle='--', label=f'Original Weighted RRF ({original_map:.4f})')
ax1.set_xlabel('k value')
ax1.set_ylabel('MAP')
ax1.set_title('MAP vs k (by rerank_depth)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: MAP vs rerank_depth (by k)
ax2 = axes[0, 1]
for k_val in sorted(df['k'].unique()):
    k_data = df[df['k'] == k_val].sort_values('rerank_depth')
    ax2.plot(k_data['rerank_depth'], k_data['MAP'], marker='o', label=f'k={k_val}')
ax2.axhline(y=original_map, color='r', linestyle='--', label=f'Original ({original_map:.4f})')
ax2.set_xlabel('rerank_depth')
ax2.set_ylabel('MAP')
ax2.set_title('MAP vs rerank_depth (by k)')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Time vs MAP (scatter)
ax3 = axes[1, 0]
scatter = ax3.scatter(df['time_s'], df['MAP'], c=df['rerank_depth'],
                     s=100, cmap='viridis', alpha=0.6)
ax3.axhline(y=original_map, color='r', linestyle='--', alpha=0.5)
ax3.set_xlabel('Time (seconds)')
ax3.set_ylabel('MAP')
ax3.set_title('Time vs MAP (colored by rerank_depth)')
plt.colorbar(scatter, ax=ax3, label='rerank_depth')
ax3.grid(True, alpha=0.3)

# Plot 4: Heatmap of MAP by k and rerank_depth
ax4 = axes[1, 1]
pivot_table = df.pivot_table(values='MAP', index='k', columns='rerank_depth')
im = ax4.imshow(pivot_table.values, cmap='RdYlGn', aspect='auto')
ax4.set_xticks(range(len(pivot_table.columns)))
ax4.set_yticks(range(len(pivot_table.index)))
ax4.set_xticklabels(pivot_table.columns)
ax4.set_yticklabels(pivot_table.index)
ax4.set_xlabel('rerank_depth')
ax4.set_ylabel('k')
ax4.set_title('MAP Heatmap (k vs rerank_depth)')

# Add values to heatmap
for i in range(len(pivot_table.index)):
    for j in range(len(pivot_table.columns)):
        if not np.isnan(pivot_table.values[i, j]):
            text = ax4.text(j, i, f'{pivot_table.values[i, j]:.4f}',
                          ha="center", va="center", color="black", fontsize=8)

plt.colorbar(im, ax=ax4, label='MAP')

plt.tight_layout()
plt.savefig('parameter_tuning_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved to: parameter_tuning_analysis.png")

print("\n" + "="*70)
