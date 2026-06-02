"""
CHUNKED TEST GENERATION FOR ROBUST04

This processes test queries in chunks and saves progress after each chunk.
If Colab disconnects, you can resume from where you left off.

Usage:
1. Set CHUNK_SIZE and START_CHUNK below
2. Run this cell - it will process one chunk and save
3. If Colab disconnects, increase START_CHUNK and re-run
"""

import time
import os
import numpy as np

# ============================================================================
# CONFIGURATION - Adjust these!
# ============================================================================
CHUNK_SIZE = 50       # Queries per chunk (50 = ~1.5 hours)
START_CHUNK = 0       # Which chunk to start from (0 = first, 1 = second, etc.)
OUTPUT_DIR = "."      # Where to save chunk files
# ============================================================================

# Calculate chunks
total_queries = len(test_qids)
num_chunks = (total_queries + CHUNK_SIZE - 1) // CHUNK_SIZE

print("="*70)
print("🔄 CHUNKED TEST GENERATION")
print("="*70)
print(f"Total test queries: {total_queries}")
print(f"Chunk size: {CHUNK_SIZE}")
print(f"Total chunks: {num_chunks}")
print(f"Starting from chunk: {START_CHUNK}")
print(f"Estimated time per chunk: ~{CHUNK_SIZE * 2:.0f} minutes")
print("="*70)

# Process requested chunk
for chunk_idx in range(START_CHUNK, num_chunks):
    start_idx = chunk_idx * CHUNK_SIZE
    end_idx = min(start_idx + CHUNK_SIZE, total_queries)
    chunk_qids = test_qids[start_idx:end_idx]
    
    chunk_file = f"{OUTPUT_DIR}/run_chunk_{chunk_idx:02d}.res"
    
    # Check if chunk already exists
    if os.path.exists(chunk_file):
        print(f"\n⏭️  Chunk {chunk_idx} already exists ({chunk_file}), skipping...")
        continue
    
    print(f"\n{'='*70}")
    print(f"📦 PROCESSING CHUNK {chunk_idx}/{num_chunks-1}")
    print(f"   Queries {start_idx+1} to {end_idx} ({len(chunk_qids)} queries)")
    print(f"{'='*70}\n")
    
    chunk_results = []
    chunk_start_time = time.time()
    
    for i, qid in enumerate(chunk_qids, 1):
        query_text = queries[qid]
        query_type = classify_query(query_text)
        
        print(f"[{i}/{len(chunk_qids)}] Query {qid} ({query_type}): {query_text[:50]}...")
        
        query_start = time.time()
        
        try:
            results = ultimate_pipeline(query_text, rerank_depth=1000)
            
            for docid, score, rank in results:
                if isinstance(score, (list, np.ndarray)):
                    score = float(score[0]) if len(score) > 0 else 0.0
                else:
                    score = float(score)
                
                chunk_results.append({
                    'qid': str(qid),
                    'docid': str(docid),
                    'rank': int(rank),
                    'score': float(score)
                })
            
            query_time = time.time() - query_start
            print(f"  ✓ Retrieved {len(results)} docs in {query_time:.1f}s")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:100]}")
            continue
        
        # Progress update every 10 queries
        if i % 10 == 0:
            elapsed = time.time() - chunk_start_time
            avg_time = elapsed / i
            remaining = (len(chunk_qids) - i) * avg_time
            print(f"\n  📊 Chunk progress: {i}/{len(chunk_qids)} | Remaining: ~{remaining/60:.1f} min\n")
    
    # Save chunk
    with open(chunk_file, 'w') as f:
        for r in chunk_results:
            f.write(f"{r['qid']} Q0 {r['docid']} {r['rank']} {r['score']:.6f} run3_chunk{chunk_idx:02d}\n")
    
    chunk_time = time.time() - chunk_start_time
    print(f"\n{'='*70}")
    print(f"✓ CHUNK {chunk_idx} COMPLETE!")
    print(f"  Saved to: {chunk_file}")
    print(f"  Queries: {len(chunk_qids)}")
    print(f"  Results: {len(chunk_results):,}")
    print(f"  Time: {chunk_time/60:.1f} minutes")
    print(f"{'='*70}")
    
    # Ask to continue or stop
    print(f"\n🔔 Chunk {chunk_idx} saved. Next chunk: {chunk_idx + 1}")
    print(f"   To continue: Re-run with START_CHUNK = {chunk_idx + 1}")
    break  # Stop after one chunk - user can re-run for next chunk

print("\n" + "="*70)
print("📝 NEXT STEPS:")
print("="*70)
print("1. Check chunk files: run_chunk_00.res, run_chunk_01.res, etc.")
print("2. To process next chunk: Set START_CHUNK = <next_number> and re-run")
print("3. When all chunks done, run the MERGE cell below")
print("="*70)
