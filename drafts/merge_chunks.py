"""
MERGE CHUNK FILES INTO FINAL RUN FILE

Run this after all chunks are complete to merge them into one file.
"""

import os
import glob

OUTPUT_DIR = "."
FINAL_FILE = "run_3_final.res"

# Find all chunk files
chunk_files = sorted(glob.glob(f"{OUTPUT_DIR}/run_chunk_*.res"))

print("="*70)
print("🔗 MERGING CHUNK FILES")
print("="*70)
print(f"Found {len(chunk_files)} chunk files:")
for f in chunk_files:
    print(f"  • {f}")

# Merge
all_results = []
for chunk_file in chunk_files:
    with open(chunk_file, 'r') as f:
        lines = f.readlines()
        all_results.extend(lines)
        print(f"  Loaded {len(lines):,} lines from {chunk_file}")

# Save merged file
with open(FINAL_FILE, 'w') as f:
    f.writelines(all_results)

print(f"\n{'='*70}")
print(f"✓ MERGED SUCCESSFULLY!")
print(f"{'='*70}")
print(f"  Output file: {FINAL_FILE}")
print(f"  Total lines: {len(all_results):,}")
print(f"\n  To evaluate:")
print(f"  python evaluate_run.py {FINAL_FILE}")
print("="*70)
