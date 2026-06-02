#!/usr/bin/env python3
"""
FINAL Parameter Tuning Analysis - Pure RRF (No Weights)
CRITICAL: These results are from PURE RRF, not weighted RRF!
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("="*70)
print("🚨 CRITICAL CLARIFICATION")
print("="*70)
print("These tuning results are from PURE RRF (no weights)!")
print("Formula: score = 1/(k+rank) for each system, then sum")
print("NOT weighted: score = w * 1/(k+rank)")
print("="*70)
print()

# All tuning results (Pure RRF, no weights)
results_data = [
    # Round 1 (k=30-60, depth=500-1000)
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
    # Round 2 (k=10-20, depth=1000-1500)
    {'k': 10, 'rerank_depth': 1000, 'MAP': 0.2759, 'nDCG@10': 0.5000, 'time_s': 2008.9},
    {'k': 10, 'rerank_depth': 1200, 'MAP': 0.2759, 'nDCG@10': 0.5000, 'time_s': 1992.0},
    {'k': 10, 'rerank_depth': 1300, 'MAP': 0.2759, 'nDCG@10': 0.5000, 'time_s': 1992.2},
    {'k': 10, 'rerank_depth': 1400, 'MAP': 0.2759, 'nDCG@10': 0.5000, 'time_s': 1993.0},
    {'k': 10, 'rerank_depth': 1500, 'MAP': 0.2759, 'nDCG@10': 0.5000, 'time_s': 1992.4},
    {'k': 20, 'rerank_depth': 1000, 'MAP': 0.2755, 'nDCG@10': 0.5017, 'time_s': 1993.1},
    {'k': 20, 'rerank_depth': 1200, 'MAP': 0.2755, 'nDCG@10': 0.5017, 'time_s': 1991.0},
    {'k': 20, 'rerank_depth': 1300, 'MAP': 0.2755, 'nDCG@10': 0.5017, 'time_s': 1991.6},
    {'k': 20, 'rerank_depth': 1400, 'MAP': 0.2755, 'nDCG@10': 0.5017, 'time_s': 1993.2},
]

df = pd.DataFrame(results_data)
df_sorted = df.sort_values('MAP', ascending=False)

print("="*70)
print("📊 PURE RRF TUNING RESULTS")
print("="*70)
print("\n🏆 TOP 5 CONFIGURATIONS:")
print("-"*70)
print(df_sorted.head(5).to_string(index=False))

# Best pure RRF config
best_pure = df_sorted.iloc[0]

# Original weighted RRF performance
original_weighted = 0.2738

print("\n\n" + "="*70)
print("🔍 COMPARISON: PURE RRF vs WEIGHTED RRF")
print("="*70)

print(f"\n1️⃣  ORIGINAL WEIGHTED RRF:")
print(f"   Configuration:")
print(f"     • W_BM25 = 1.0, W_RM3 = 1.5, W_MONOT5 = 2.0")
print(f"     • k = 30")
print(f"     • rerank_depth = 300")
print(f"   Performance: MAP = {original_weighted:.4f}")

print(f"\n2️⃣  BEST PURE RRF (from tuning):")
print(f"   Configuration:")
print(f"     • No weights (equal treatment)")
print(f"     • k = {int(best_pure['k'])}")
print(f"     • rerank_depth = {int(best_pure['rerank_depth'])}")
print(f"   Performance: MAP = {best_pure['MAP']:.4f}")

improvement = best_pure['MAP'] - original_weighted
print(f"\n📊 VERDICT:")
print(f"   Difference: {improvement:+.4f} ({improvement/original_weighted*100:+.2f}%)")

if improvement > 0:
    print(f"   ✅ Pure RRF (k={int(best_pure['k'])}) is BETTER by {improvement:.4f}!")
    winner = "PURE_RRF"
else:
    print(f"   ⚠️  Weighted RRF is still BETTER by {-improvement:.4f}")
    winner = "WEIGHTED_RRF"

print("\n" + "="*70)
print("💡 KEY INSIGHTS")
print("="*70)

print(f"\n1. OPTIMAL k FOR PURE RRF:")
print(f"   • k=10 gives best results (0.2759)")
print(f"   • Much lower than Cormack's k=60 recommendation")
print(f"   • Reason: Your system has strong neural reranker (MonoT5)")
print(f"   • Lower k = more emphasis on top-ranked docs")

print(f"\n2. RERANK DEPTH:")
print(f"   • depth=1000 is optimal")
print(f"   • No improvement beyond 1000")
print(f"   • All k=10 configs with depth≥1000 have same MAP (0.2759)")

print(f"\n3. PURE vs WEIGHTED RRF:")
if winner == "PURE_RRF":
    print(f"   ✅ Pure RRF (k=10) wins!")
    print(f"   • Weighted RRF: 0.2738")
    print(f"   • Pure RRF: 0.2759")
    print(f"   • Advantage: +0.0021 (+0.77%)")
else:
    print(f"   ⚠️  Weighted RRF still better")
    print(f"   • But the gap is small (only {-improvement:.4f})")
    print(f"   • Consider: What k would work for weighted RRF?")

print("\n" + "="*70)
print("🎯 FINAL RECOMMENDATIONS")
print("="*70)

if winner == "PURE_RRF":
    print("\n✅ RECOMMENDED APPROACH: Pure RRF with k=10")
    print("\n📋 Configuration:")
    print("   • Method: Pure RRF (no weights)")
    print("   • k = 10")
    print("   • rerank_depth = 1000")
    print("   • Systems: BM25 + RM3 + MonoT5")
    print(f"   • Expected MAP: ~0.276")
else:
    print("\n✅ RECOMMENDED APPROACH: Weighted RRF with k=10")
    print("\n📋 Configuration:")
    print("   • Method: Weighted RRF")
    print("   • Weights: W_BM25=1.0, W_RM3=1.5, W_MONOT5=2.0")
    print("   • k = 10 (apply to weighted version!)")
    print("   • rerank_depth = 1000")
    print(f"   • Expected MAP: ~0.278-0.282 (better than both!)")

print("\n🚀 NEXT STEPS TO REACH MAP 0.35:")
print("\n   Phase 1: Apply optimal k=10 + depth=1000")
print(f"   → Expected: ~0.278-0.282")
print("\n   Phase 2: Add SPLADE (4th signal)")
print("   → Expected boost: +0.05-0.07")
print("   → Expected total: ~0.33-0.35 ✅")
print("\n   Phase 3: Fine-tune SPLADE weight")
print("   → Push to 0.35+")

print("\n" + "="*70)
print("🧪 EXPERIMENT RECOMMENDATION")
print("="*70)

print("\nTest both approaches with k=10 on training set:")
print("\n1️⃣  Pure RRF (k=10, depth=1000):")
print("   Expected: 0.2759 (validated)")
print("\n2️⃣  Weighted RRF (k=10, depth=1000):")
print("   Expected: 0.278-0.282 (hypothesis)")
print("   Weights: W_BM25=1.0, W_RM3=1.5, W_MONOT5=2.0")
print("\nPick the winner, then add SPLADE!")

print("\n" + "="*70)
print("📈 PERFORMANCE TRAJECTORY")
print("="*70)

print(f"\n  Baseline:")
print(f"    Original (weighted, k=30, d=300): 0.2738")
print(f"    Pure RRF (k=10, d=1000): 0.2759 ✅")
print(f"\n  With k=10 optimization:")
print(f"    Weighted RRF (k=10, d=1000): ~0.278-0.282 (est.)")
print(f"\n  + SPLADE (4-way fusion):")
print(f"    Expected: ~0.33-0.35 🎯")
print(f"\n  Target: 0.35 MAP")

print("\n" + "="*70)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: MAP vs k
ax1 = axes[0, 0]
k_summary = df.groupby('k')['MAP'].agg(['mean', 'max']).reset_index()
x = np.arange(len(k_summary))
width = 0.35
bars1 = ax1.bar(x - width/2, k_summary['mean'], width, label='Avg MAP', color='skyblue', edgecolor='black')
bars2 = ax1.bar(x + width/2, k_summary['max'], width, label='Max MAP', color='orange', edgecolor='black')
ax1.axhline(y=original_weighted, color='red', linestyle='--', linewidth=2.5, label=f'Weighted RRF (0.2738)')
ax1.set_xlabel('k value', fontsize=12, fontweight='bold')
ax1.set_ylabel('MAP', fontsize=12, fontweight='bold')
ax1.set_title('Pure RRF: MAP by k value', fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([f'k={int(k)}' for k in k_summary['k']])
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}',
                ha='center', va='bottom', fontsize=8)

# Plot 2: MAP vs rerank_depth for k=10
ax2 = axes[0, 1]
k10_data = df[df['k'] == 10].sort_values('rerank_depth')
ax2.plot(k10_data['rerank_depth'], k10_data['MAP'], marker='o', linewidth=2.5,
         markersize=10, color='green', label='Pure RRF (k=10)')
ax2.axhline(y=original_weighted, color='red', linestyle='--', linewidth=2, label=f'Weighted RRF')
ax2.fill_between(k10_data['rerank_depth'], k10_data['MAP'], original_weighted,
                  where=(k10_data['MAP'] > original_weighted), alpha=0.3, color='green',
                  label='Improvement over weighted')
ax2.set_xlabel('rerank_depth', fontsize=12, fontweight='bold')
ax2.set_ylabel('MAP', fontsize=12, fontweight='bold')
ax2.set_title('Pure RRF (k=10): Effect of rerank_depth', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_ylim([0.272, 0.277])

# Plot 3: Complete heatmap
ax3 = axes[1, 0]
pivot = df.pivot_table(values='MAP', index='k', columns='rerank_depth', aggfunc='first')
im = ax3.imshow(pivot.values, cmap='RdYlGn', aspect='auto', vmin=0.26, vmax=0.28)
ax3.set_xticks(range(len(pivot.columns)))
ax3.set_yticks(range(len(pivot.index)))
ax3.set_xticklabels([int(d) for d in pivot.columns], rotation=45)
ax3.set_yticklabels([int(k) for k in pivot.index])
ax3.set_xlabel('rerank_depth', fontsize=12, fontweight='bold')
ax3.set_ylabel('k', fontsize=12, fontweight='bold')
ax3.set_title('Pure RRF: Complete MAP Heatmap', fontsize=13, fontweight='bold')

# Add best marker
best_k_idx = list(pivot.index).index(best_pure['k'])
best_d_idx = list(pivot.columns).index(best_pure['rerank_depth'])
ax3.scatter(best_d_idx, best_k_idx, s=300, marker='*', color='yellow',
            edgecolors='black', linewidths=2, label='Best', zorder=10)
ax3.legend(fontsize=10)

for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        if not np.isnan(pivot.values[i, j]):
            color = 'white' if pivot.values[i, j] < 0.27 else 'black'
            ax3.text(j, i, f'{pivot.values[i, j]:.4f}',
                    ha="center", va="center", color=color, fontsize=8, fontweight='bold')

plt.colorbar(im, ax=ax3, label='MAP')

# Plot 4: Performance trajectory
ax4 = axes[1, 1]
stages = ['Original\nWeighted\nk=30, d=300',
          'Pure RRF\nk=10, d=1000\n(validated)',
          'Weighted RRF\nk=10, d=1000\n(estimated)',
          '+ SPLADE\n4-way\n(target)']
maps = [0.2738, 0.2759, 0.280, 0.350]
colors = ['lightblue', 'lightgreen', 'yellow', 'gold']
bars = ax4.bar(stages, maps, color=colors, edgecolor='black', linewidth=2)

# Target line
ax4.axhline(y=0.35, color='red', linestyle='--', linewidth=2, label='Target (0.35)')

# Value labels
for bar, val in zip(bars, maps):
    height = bar.get_height()
    label = f'{val:.4f}' if val < 0.35 else f'{val:.3f} 🎯'
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.002,
            label, ha='center', va='bottom', fontsize=11, fontweight='bold')

ax4.set_ylabel('MAP', fontsize=12, fontweight='bold')
ax4.set_title('Performance Trajectory to MAP 0.35', fontsize=13, fontweight='bold')
ax4.set_ylim([0.25, 0.37])
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('parameter_tuning_final.png', dpi=300, bbox_inches='tight')
print("\n✓ Final visualization saved to: parameter_tuning_final.png")

df_sorted.to_csv('parameter_tuning_pure_rrf.csv', index=False)
print("✓ Results saved to: parameter_tuning_pure_rrf.csv")

print("\n" + "="*70)
