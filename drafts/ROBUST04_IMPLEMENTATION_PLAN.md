# ROBUST04 Text Retrieval Competition - Implementation Plan

## Objective
Build an advanced search engine to achieve the highest MAP score on ROBUST04 collection (249 queries, 199 test queries).

---

## Research Summary

### Current State-of-the-Art (2024-2025)
- **MonoT5-3B** (zero-shot): MAP = 0.273
- **KeyB2** (LLM-based reranking): SOTA on TREC DL 2019
- **BM25 baseline**: MAP = 0.253
- **MonoBERT**: MAP = 0.210
- **E5-large-v2**: MAP = 0.174

### Key Techniques Identified
1. **Query Expansion**: RM3 pseudo-relevance feedback
2. **Hybrid Retrieval**: Combining BM25, QL, and dense retrieval
3. **Reciprocal Rank Fusion**: Combining multiple ranked lists
4. **Neural Reranking**: Cross-encoders, MonoBERT, BGE Reranker
5. **Parameter Tuning**: Grid search on first 50 queries

---

## Three-Run Strategy

### **Run 1: Optimized BM25 + RM3** ✅ (Recommended as primary)
**Goal**: Strong, reliable baseline with query expansion

**Algorithm**:
1. Use Pyserini BM25 with Porter stemming (matches index)
2. Apply RM3 pseudo-relevance feedback
3. Tune parameters on first 50 queries using grid search

**Parameters to Tune**:
- BM25 `k1`: [0.6, 0.9, 1.2, 1.5, 1.8] (default: 0.9)
- BM25 `b`: [0.4, 0.6, 0.75, 0.8, 0.9] (default: 0.4)
- RM3 `fb_docs`: [5, 10, 15, 20, 25, 30]
- RM3 `fb_terms`: [20, 40, 60, 80, 100]
- RM3 `original_query_weight`: [0.1, 0.3, 0.5, 0.7, 0.9]

**Expected MAP**: 0.26 - 0.28 (based on literature)

**Implementation Steps**:
```python
from pyserini.search.lucene import LuceneSearcher
searcher = LuceneSearcher.from_prebuilt_index('robust04')
searcher.set_bm25(k1=X, b=Y)
searcher.set_rm3(fb_docs=A, fb_terms=B, original_query_weight=C)
```

---

### **Run 2: Hybrid Retrieval + Reciprocal Rank Fusion**
**Goal**: Combine multiple retrieval methods for robustness

**Algorithm**:
1. Retrieve top 1000 using 3 different methods:
   - BM25 (optimized parameters)
   - BM25 + RM3 (different parameters than Run 1)
   - Query Language Model (QL/Dirichlet)
2. Apply Reciprocal Rank Fusion (RRF) to combine rankings

**RRF Formula**:
```
RRF_score(d) = Σ(1 / (k + rank_i(d)))
where k is typically 60, rank_i(d) is rank of document d in list i
```

**Parameters to Tune**:
- RRF constant `k`: [30, 60, 90]
- Weight distribution across methods (if using weighted RRF)
- Individual method parameters

**Expected MAP**: 0.27 - 0.29 (RRF typically gives 2-5% improvement)

**Implementation Steps**:
```python
# Retrieve from multiple methods
results_bm25 = searcher1.search(query, k=1000)
results_rm3 = searcher2.search(query, k=1000)
results_ql = searcher3.search(query, k=1000)

# Apply RRF
def reciprocal_rank_fusion(ranked_lists, k=60):
    scores = defaultdict(float)
    for ranked_list in ranked_lists:
        for rank, doc_id in enumerate(ranked_list, start=1):
            scores[doc_id] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

---

### **Run 3: Neural Reranking or Advanced Score Fusion**
**Goal**: Maximize performance with state-of-the-art techniques

**Option A: Neural Reranking** (if GPU available)
1. First-stage retrieval: BM25 retrieves top 100 candidates
2. Second-stage reranking: Use cross-encoder (MonoBERT, BGE Reranker)
3. Return top 1000 from reranked results

**Models to Consider**:
- **MonoBERT** (requires GPU, MAP ~0.210)
- **BGE Reranker** (BAAI, open-source, hosted on HuggingFace)
- **MiniLM cross-encoder** (lightweight)

**Option B: Advanced Score Fusion** (if no GPU)
1. Retrieve using 3-4 methods with different parameters
2. Normalize scores using min-max or z-score
3. Apply weighted linear combination
4. Use query classification to set weights dynamically

**Fusion Formula**:
```
score(d) = α·BM25(d) + β·RM3(d) + γ·QL(d)
where α + β + γ = 1
```

**Expected MAP**:
- Neural reranking: 0.28 - 0.30+
- Score fusion: 0.27 - 0.29

---

## Implementation Workflow

### **Phase 1: Setup and Data Loading**
```python
# Install dependencies
!pip install pyserini ir_measures

# Load queries and qrels
queries = load_queries('queriesROBUST.txt')  # 249 queries
qrels = load_qrels('qrels_50_Queries')  # First 50 queries

# Split data
train_queries = queries[:50]  # For tuning
test_queries = queries[50:]   # 199 queries for submission
```

### **Phase 2: Parameter Tuning (on first 50 queries)**
```python
import ir_measures
from ir_measures import MAP, nDCG

# Grid search for Run 1
best_map = 0
best_params = {}

for k1 in [0.6, 0.9, 1.2, 1.5]:
    for b in [0.4, 0.6, 0.75, 0.9]:
        for fb_docs in [10, 20, 30]:
            for fb_terms in [40, 60, 80]:
                for orig_weight in [0.3, 0.5, 0.7]:
                    # Configure searcher
                    searcher.set_bm25(k1=k1, b=b)
                    searcher.set_rm3(fb_docs, fb_terms, orig_weight)

                    # Evaluate on train queries
                    results = evaluate(searcher, train_queries, qrels)
                    map_score = results[MAP]

                    if map_score > best_map:
                        best_map = map_score
                        best_params = {...}
```

### **Phase 3: Generate Runs**
```python
# Run 1: Optimized BM25 + RM3
run1_results = generate_run(test_queries, best_params_run1)
save_trec_format(run1_results, 'run_1.res', run_tag='run1')

# Run 2: Hybrid + RRF
run2_results = generate_hybrid_rrf_run(test_queries)
save_trec_format(run2_results, 'run_2.res', run_tag='run2')

# Run 3: Neural reranking or Score fusion
run3_results = generate_advanced_run(test_queries)
save_trec_format(run3_results, 'run_3.res', run_tag='run3')
```

### **Phase 4: Output Format (TREC 6-column)**
```
630 Q0 ZF08-175-870 1 0.7 run1
630 Q0 ZF08-306-044 2 0.5 run1
630 Q0 ZF09-477-757 3 0.3 run1
...
```

---

## Advanced Techniques to Explore

### **1. Query Classification**
- Classify queries as navigational vs exploratory
- Use different α weights in fusion based on query type
- Navigational (e.g., "Facebook login"): α=0.8 for BM25
- Exploratory (e.g., "AI ethics"): α=0.3 for BM25

### **2. Document Length Normalization**
- ROBUST04 contains news articles with varying lengths
- Tune BM25 `b` parameter carefully (higher b = more length normalization)

### **3. Pseudo-Relevance Feedback Filtering**
- Instead of using all top-k documents for RM3, filter by:
  - Minimum BM25 score threshold
  - K-means clustering to select diverse documents

### **4. Score Normalization**
- Min-max normalization: (score - min) / (max - min)
- Z-score normalization: (score - mean) / std
- Essential for score fusion to work properly

---

## Tools and Libraries

### **Required**:
- `pyserini`: For BM25, RM3, and index access
- `ir_measures`: For MAP evaluation

### **Optional** (for advanced techniques):
- `transformers`: For neural reranking models
- `sentence-transformers`: For cross-encoders
- `faiss`: For dense retrieval (if using embeddings)
- `torch`: For PyTorch models

---

## Evaluation Strategy

### **On Training Set (50 queries)**:
- Use `ir_measures` to compute MAP
- Also monitor: P@10, nDCG@10, MRR
- Perform 5-fold cross-validation if needed

### **On Test Set (199 queries)**:
- Submit 3 runs as specified
- Expected MAP range: 0.26 - 0.30 (competitive)
- Top teams might achieve 0.28 - 0.32+

---

## Risk Mitigation

### **If Neural Reranking is Too Slow**:
- Use CPU-friendly cross-encoders (MiniLM)
- Reduce candidate set size (top 50 instead of 100)
- Use score fusion instead

### **If RM3 Doesn't Improve MAP**:
- Check if index supports document vectors
- Try reducing fb_docs (use fewer feedback documents)
- Try different original_query_weight values

### **If Fusion Degrades Performance**:
- Check score normalization
- Use fewer methods (2-3 instead of 4-5)
- Try simpler fusion (RRF instead of weighted)

---

## Timeline Estimate

1. **Setup and baseline**: 1-2 hours
2. **Parameter tuning**: 2-4 hours (depends on grid size)
3. **Run 1 implementation**: 1 hour
4. **Run 2 implementation**: 2-3 hours
5. **Run 3 implementation**: 3-5 hours (depends on approach)
6. **Testing and validation**: 1-2 hours

**Total**: 10-17 hours

---

## Key References

Based on 2024-2025 research:

1. **MonoT5 and Neural Ranking**: "From Neural Re-Ranking to Neural Ranking" (Zamani et al.)
2. **KeyB2 Reranking**: "KeyB2: Selecting Key Blocks is Also Important for Long Document Ranking with Large Language Models" (2024)
3. **Hybrid Retrieval Best Practices**: "Building effective hybrid search in OpenSearch" (2025)
4. **Reciprocal Rank Fusion**: Original RRF paper (Cormack & Clarke, 2009) + 2025 TREC iKAT applications
5. **RM3 Parameters**: Pyserini documentation and SPLADE+RM3 tuning studies
6. **Neural Reranking**: "A Deep Look into Neural Ranking Models for Information Retrieval" (Guo et al.)

---

## Success Metrics

- **Minimum Goal**: MAP > 0.26 (beat BM25 baseline)
- **Target Goal**: MAP > 0.28 (competitive performance)
- **Stretch Goal**: MAP > 0.30 (top-tier performance)

Good luck! 🚀
