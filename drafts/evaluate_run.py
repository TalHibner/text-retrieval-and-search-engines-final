#!/usr/bin/env python3
"""
Quick MAP Evaluation Script for ROBUST04

Usage:
    python evaluate_run.py <run_file>
    
Example:
    python evaluate_run.py run_3_final.res
"""

import sys
from collections import defaultdict

def load_qrels(qrel_file):
    """Load qrels file (format: qid iter docid rel)"""
    qrels = defaultdict(dict)
    with open(qrel_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 4:
                qid, _, docid, rel = parts[0], parts[1], parts[2], int(parts[3])
                qrels[qid][docid] = rel
    return qrels

def load_run(run_file):
    """Load run file (format: qid Q0 docid rank score run_name)"""
    runs = defaultdict(list)
    with open(run_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 5:
                qid, _, docid, rank, score = parts[0], parts[1], parts[2], int(parts[3]), float(parts[4])
                runs[qid].append((docid, rank, score))
    
    # Sort by rank
    for qid in runs:
        runs[qid].sort(key=lambda x: x[1])
    
    return runs

def compute_ap(ranked_docs, qrel_docs):
    """Compute Average Precision for a single query"""
    if not qrel_docs:
        return 0.0
    
    # Count relevant documents
    num_relevant = sum(1 for rel in qrel_docs.values() if rel > 0)
    if num_relevant == 0:
        return 0.0
    
    relevant_count = 0
    precision_sum = 0.0
    
    for rank, (docid, _, _) in enumerate(ranked_docs, 1):
        if docid in qrel_docs and qrel_docs[docid] > 0:
            relevant_count += 1
            precision_at_rank = relevant_count / rank
            precision_sum += precision_at_rank
    
    return precision_sum / num_relevant

def compute_map(runs, qrels):
    """Compute Mean Average Precision"""
    aps = []
    missing_queries = 0
    
    for qid in sorted(qrels.keys()):
        if qid in runs:
            ap = compute_ap(runs[qid], qrels[qid])
            aps.append(ap)
        else:
            missing_queries += 1
            aps.append(0.0)
    
    if not aps:
        return 0.0, 0, missing_queries
    
    return sum(aps) / len(aps), len(aps), missing_queries

def compute_precision_at_k(runs, qrels, k=10):
    """Compute Precision at k"""
    precisions = []
    
    for qid in sorted(qrels.keys()):
        if qid in runs:
            top_k = runs[qid][:k]
            relevant_in_top_k = sum(1 for docid, _, _ in top_k 
                                    if docid in qrels[qid] and qrels[qid][docid] > 0)
            precisions.append(relevant_in_top_k / k)
        else:
            precisions.append(0.0)
    
    return sum(precisions) / len(precisions) if precisions else 0.0

def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate_run.py <run_file>")
        print("Example: python evaluate_run.py run_3_final.res")
        sys.exit(1)
    
    run_file = sys.argv[1]
    qrel_file = 'qrels.robust2004.txt'
    
    print("="*60)
    print("ROBUST04 Evaluation")
    print("="*60)
    print(f"Run file: {run_file}")
    print(f"Qrels file: {qrel_file}")
    print("="*60)
    
    # Load files
    print("\nLoading files...")
    try:
        qrels = load_qrels(qrel_file)
        print(f"  Qrels: {len(qrels)} queries")
    except FileNotFoundError:
        print(f"  ERROR: {qrel_file} not found!")
        sys.exit(1)
    
    try:
        runs = load_run(run_file)
        print(f"  Run: {len(runs)} queries")
    except FileNotFoundError:
        print(f"  ERROR: {run_file} not found!")
        sys.exit(1)
    
    # Compute metrics
    print("\nComputing metrics...")
    map_score, num_queries, missing = compute_map(runs, qrels)
    p10 = compute_precision_at_k(runs, qrels, k=10)
    p20 = compute_precision_at_k(runs, qrels, k=20)
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  MAP:       {map_score:.4f}  ← Main metric")
    print(f"  P@10:      {p10:.4f}")
    print(f"  P@20:      {p20:.4f}")
    print(f"  Queries:   {num_queries}")
    if missing > 0:
        print(f"  Missing:   {missing}")
    print("="*60)
    
    # Performance assessment
    print("\n📈 Performance Assessment:")
    if map_score >= 0.35:
        print("  🌟 EXCELLENT! Top-tier performance!")
    elif map_score >= 0.30:
        print("  ✓ GREAT! Strong performance!")
    elif map_score >= 0.28:
        print("  ✓ GOOD! Solid performance!")
    elif map_score >= 0.25:
        print("  ⚠️  OK - room for improvement")
    else:
        print("  ⚠️  Below expected - check configuration")
    print("="*60)

if __name__ == "__main__":
    main()
