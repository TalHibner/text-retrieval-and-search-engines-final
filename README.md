# 🔍 Text Retrieval & Search Engines — Final Project

> **ROBUST04 Ad-Hoc Retrieval Competition**  
> A multi-run information retrieval system combining BM25, neural reranking, query expansion, and ensemble fusion on the TREC ROBUST04 benchmark.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [Repository Structure](#-repository-structure)
- [Retrieval Runs](#-retrieval-runs)
- [Techniques](#-techniques)
- [Installation & Setup](#-installation--setup)
- [Configuration Variables](#-configuration-variables)
- [Usage](#-usage)
- [Evaluation](#-evaluation)
- [Results](#-results)
- [Utility Scripts](#-utility-scripts)
- [References](#-references)

---

## 📖 Project Overview

This project implements a competitive ad-hoc document retrieval system over the **ROBUST04** collection — a standard TREC benchmark of ~528,000 newswire articles with 249 queries (50 training, 199 test).

The system is structured around **three submission runs** of increasing sophistication:

| Run | Strategy | Key Technique | Expected MAP |
|-----|----------|---------------|-------------|
| **Run 1** | Optimized BM25 + RM3 | Grid-searched parameters + pseudo-relevance feedback | 0.26 – 0.28 |
| **Run 2** | Hybrid Retrieval + RRF | Reciprocal Rank Fusion over multiple BM25 variants | 0.27 – 0.29 |
| **Run 3** | Neural Ensemble Reranking | Qwen 8B + Cohere Rerank v3 + Groq Llama 3.3-70B | 0.28 – 0.33 |

All runs output results in standard **TREC 6-column format** ready for official evaluation.

---

## 📁 Repository Structure

```
.
├── data/
│   ├── queriesROBUST.txt          # 249 queries (50 train + 199 test)
│   ├── qrels_50_Queries           # Relevance judgments for 50 training queries
│   └── qrels.robust2004.txt       # Full qrels for all 249 queries
│
├── results/
│   ├── run_1.res                  # Run 1 output (BM25 + RM3)
│   ├── run_2.res                  # Run 2 output (Hybrid RRF)
│   ├── run_3.res                  # Run 3 output (Neural Ensemble)
│   ├── 10/                        # Run 3 chunked output (chunk size 10)
│   └── 30/                        # Run 3 chunked output (chunk size 30)
│
├── drafts/                        # Development notebooks and scripts
│   ├── ROBUST04_Phase1_Fixed.ipynb              # Run 1: BM25 + RM3
│   ├── ROBUST04_Run2_Hybrid_RRF.ipynb           # Run 2: Hybrid RRF
│   ├── ROBUST04_Run3_Ensemble.ipynb             # Run 3: Full neural ensemble (Groq)
│   ├── ROBUST04_FINAL.ipynb                     # Consolidated final submission
│   ├── ROBUST04_FINAL_ULTIMATE.ipynb            # Best optimized pipeline
│   ├── GT_Q2D_NoLLM_Advanced_Retrieval.ipynb   # ⭐ Recommended: neural, no API costs
│   ├── GT_Q2D_Advanced_Retrieval.ipynb          # LLM-based Query2Doc expansion
│   ├── GT_Q2D_Data_Gathering.ipynb              # Q2D data collection (DeepSeek)
│   ├── evaluate_run.py                          # Standalone MAP evaluation script
│   ├── chunked_generation.py                    # Fault-tolerant chunked generation
│   ├── merge_chunks.py                          # Merge chunked .res files
│   ├── parameter_tuning_*.py                    # Grid search analysis scripts
│   └── ADVANCED_RETRIEVAL_SUMMARY.md            # Technique comparison guide
│
├── Final_Part_A_Ranking_Challenge.pdf  # Assignment spec (Part A)
├── Final_Project_PART_B.pdf            # Assignment spec (Part B)
├── Final_Project_PART_B-our-solution.pdf  # Our written solution
├── seeded_llm_tournament.pdf           # LLM tournament design doc
└── README.md
```

---

## 🏃 Retrieval Runs

### Run 1 — Optimized BM25 + RM3
**Notebook:** [`ROBUST04_Phase1_Fixed.ipynb`](drafts/ROBUST04_Phase1_Fixed.ipynb)

Standard BM25 retrieval with RM3 pseudo-relevance feedback. Parameters are tuned via grid search on the 50 training queries before applying to the 199 test queries.

**Tuned parameters:**
- BM25 `k1` ∈ {0.6, 0.9, 1.2, 1.5, 1.8}
- BM25 `b` ∈ {0.4, 0.6, 0.75, 0.8, 0.9}
- RM3 `fb_docs` ∈ {5, 10, 15, 20, 25, 30}
- RM3 `fb_terms` ∈ {20, 40, 60, 80, 100}
- RM3 `original_query_weight` ∈ {0.1, 0.3, 0.5, 0.7, 0.9}

---

### Run 2 — Hybrid Retrieval + Reciprocal Rank Fusion
**Notebook:** [`ROBUST04_Run2_Hybrid_RRF.ipynb`](drafts/ROBUST04_Run2_Hybrid_RRF.ipynb)

Three BM25 variants (different parameters) are fused using RRF:

```
RRF_score(d) = Σᵢ [ 1 / (k + rankᵢ(d)) ]   where k = 60
```

This rank-based fusion is robust to score-scale differences across retrieval methods.

---

### Run 3 — Neural Ensemble Reranking
**Notebook:** [`ROBUST04_Run3_Ensemble.ipynb`](drafts/ROBUST04_Run3_Ensemble.ipynb)

A three-model ensemble reranker applied on top of BM25 first-stage retrieval:

| Model | Type | Weight | Provider |
|-------|------|--------|----------|
| Qwen3-Reranker-8B (INT8) | Cross-encoder | 1.5 | HuggingFace |
| Cohere Rerank v3 | Purpose-built reranker | 1.3 | Cohere API |
| Llama 3.3-70B | Listwise LLM ranker | 1.2 | Groq API |

Final score: `score = 1.5·Qwen + 1.3·Cohere + 1.2·Groq`

---

## 🧠 Techniques

### Neural Cross-Encoder Reranking
Pre-trained cross-encoders score each (query, document) pair jointly, enabling deep semantic matching beyond keyword overlap:
- `Qwen/Qwen3-Reranker-8B` — primary, 8-bit quantized for T4 GPU
- `BAAI/bge-reranker-v2-m3` — fallback
- `cross-encoder/ms-marco-MiniLM-L-6-v2` — lightweight fallback

### RM3 Pseudo-Relevance Feedback
Automatic query expansion using top-retrieved document vocabulary (no LLM required):
```
expanded_query = α · original_query + (1-α) · Σ(top_term_weights)
```

### Query2Doc (Q2D) Expansion
LLM-generated pseudo-documents expand the query signal before BM25 retrieval. Implemented with DeepSeek-R1-Distill-Qwen-7B locally.

### Reciprocal Rank Fusion (RRF)
Rank-based combination of heterogeneous retrieval lists, robust to score normalization issues:
```
RRF_score(d) = Σ [ 1 / (60 + rank_i(d)) ]
```

### Hybrid Weighted Fusion
Grid-search optimized weighted combination of all retrieval signals:
```
final_score = w₁·BM25 + w₂·RM3 + w₃·Ensemble + w₄·Neural
```

---

## ⚙️ Installation & Setup

### 1. Environment
The notebooks are designed to run on **Google Colab** (free T4 GPU). All heavy dependencies are installed inline.

For local execution:

```bash
pip install pyserini ir_measures transformers torch sentence-transformers faiss-cpu
```

> **Java required:** Pyserini depends on Java 11+. Install via `apt-get install openjdk-21-jdk` on Linux.

### 2. ROBUST04 Index
Pyserini auto-downloads the pre-built ROBUST04 index on first use:

```python
from pyserini.search.lucene import LuceneSearcher
searcher = LuceneSearcher.from_prebuilt_index('robust04')
```

### 3. API Keys (Run 3 only)
Run 3 requires API keys for Cohere and Groq. Set them as **Colab Secrets** (or environment variables locally):

| Variable | Service | Get Key |
|----------|---------|---------|
| `HF_TOKEN` | HuggingFace | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `COHERE_API_KEY` | Cohere Rerank | [dashboard.cohere.com](https://dashboard.cohere.com/) |
| `GROQ_API_KEY` | Groq (Llama) | [console.groq.com](https://console.groq.com/) |

> ⚠️ **Never hardcode API keys** in notebooks. Always load from environment variables or Colab Secrets:
> ```python
> from google.colab import userdata
> COHERE_API_KEY = userdata.get('COHERE_API_KEY')
> ```

---

## 🔧 Configuration Variables

### BM25 Parameters
| Variable | Default | Description |
|----------|---------|-------------|
| `k1` | `0.9` | Term frequency saturation |
| `b` | `0.4` | Document length normalization |

### RM3 Parameters
| Variable | Default | Description |
|----------|---------|-------------|
| `fb_docs` | `10` | Number of feedback documents |
| `fb_terms` | `10` | Number of expansion terms |
| `original_query_weight` | `0.5` | Weight of original query (α) |

### RRF Parameters
| Variable | Default | Description |
|----------|---------|-------------|
| `k` | `60` | RRF constant (rank smoothing) |

### Neural Reranking Parameters
| Variable | Default | Description |
|----------|---------|-------------|
| `rerank_depth` | `100` | Number of BM25 candidates to rerank |
| `batch_size` | `8` | Inference batch size for cross-encoder |
| `max_length` | `512` | Max token length for model inputs |

### Ensemble Weights
| Variable | Default | Description |
|----------|---------|-------------|
| `QWEN_WEIGHT` | `1.5` | Weight for Qwen cross-encoder scores |
| `COHERE_WEIGHT` | `1.3` | Weight for Cohere reranker scores |
| `GROQ_WEIGHT` | `1.2` | Weight for Groq LLM listwise scores |

### Chunked Generation
| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | `50` | Queries processed per chunk |
| `START_CHUNK` | `0` | Resume from this chunk index |
| `OUTPUT_DIR` | `"."` | Directory to save chunk `.res` files |

---

## 🚀 Usage

### Option A: No-LLM Pipeline (Recommended — fastest, $0 cost)

```python
# Open in Colab:
# drafts/GT_Q2D_NoLLM_Advanced_Retrieval.ipynb

# Pipeline summary:
# 1. BM25 with tuned parameters
# 2. RM3 pseudo-relevance feedback
# 3. Multi-parameter BM25 ensemble
# 4. Neural cross-encoder reranking (MiniLM / MonoT5)
# 5. RRF fusion
# 6. Grid-search weight optimization
# → Outputs: run_3_final.res
```

**Expected time:** 30–60 minutes on free Colab GPU  
**Cost:** $0

---

### Option B: Full Neural Ensemble (Run 3, best MAP)

```python
# Open in Colab:
# drafts/ROBUST04_Run3_Ensemble.ipynb

# Requires Colab Secrets:
#   COHERE_API_KEY, GROQ_API_KEY, HF_TOKEN

# Pipeline summary:
# 1. BM25 first-stage retrieval (top 1000)
# 2. Qwen 8B cross-encoder reranking
# 3. Cohere Rerank v3 (API)
# 4. Groq Llama 3.3-70B listwise ranking (API)
# 5. Weighted ensemble fusion
# → Outputs: run_3.res
```

**Expected time:** 30–40 minutes on Colab GPU (with Groq rate-limit retries)  
**Cost:** ~$0.02 for 249 queries

---

### Option C: Chunked Generation (for long/interrupted runs)

If Colab disconnects mid-run, use the chunked approach:

```bash
# In drafts/chunked_generation.py, set:
CHUNK_SIZE = 50      # queries per chunk
START_CHUNK = 0      # start from chunk 0

# After disconnection, resume:
START_CHUNK = 2      # resume from chunk 2
```

Then merge all chunks:

```bash
python merge_chunks.py
```

---

## 📊 Evaluation

### Quick Evaluation Script

```bash
cd data/
python ../drafts/evaluate_run.py ../results/run_3.res
```

**Output:**
```
============================================================
ROBUST04 Evaluation
============================================================
Run file: ../results/run_3.res
Qrels file: qrels.robust2004.txt
============================================================

📊 RESULTS
============================================================
  MAP:       0.3142  ← Main metric
  P@10:      0.4221
  P@20:      0.3560
  Queries:   249
============================================================

📈 Performance Assessment:
  ✓ GREAT! Strong performance!
============================================================
```

### Metrics Reported
| Metric | Description |
|--------|-------------|
| **MAP** | Mean Average Precision — primary competition metric |
| **P@10** | Precision at rank 10 |
| **P@20** | Precision at rank 20 |

### Performance Targets
| MAP | Assessment |
|-----|------------|
| ≥ 0.35 | 🌟 Excellent — top-tier |
| ≥ 0.30 | ✅ Great — strong |
| ≥ 0.28 | ✅ Good — solid |
| ≥ 0.25 | ⚠️ OK — room for improvement |
| < 0.25 | ⚠️ Below baseline |

---

## 📈 Results

Expected performance based on literature and observed runs:

| Pipeline | MAP (est.) | vs. BM25 Baseline |
|----------|-----------|-------------------|
| BM25 baseline | ~0.253 | — |
| Run 1: BM25 + RM3 (tuned) | 0.26 – 0.28 | +3–10% |
| Run 2: Hybrid RRF | 0.27 – 0.29 | +7–15% |
| Run 3: Neural Ensemble | 0.28 – 0.33 | +11–30% |
| No-LLM Advanced (recommended) | 0.30 – 0.35 | +20–38% |

> **Key insight:** Neural cross-encoder reranking alone provides the largest single gain (+10–15% MAP), often exceeding the contribution of LLM query expansion.

---

## 🛠️ Utility Scripts

### `evaluate_run.py`
Standalone MAP evaluator — no external dependencies beyond the standard library.

```bash
python drafts/evaluate_run.py <run_file>
# Example:
python drafts/evaluate_run.py results/run_1.res
```

### `chunked_generation.py`
Fault-tolerant batch processor. Saves one chunk at a time and skips already-completed chunks on resume.

```python
CHUNK_SIZE = 50     # ~1.5 hours per chunk on Colab
START_CHUNK = 0     # set to 1, 2, 3... to resume
```

### `merge_chunks.py`
Merges `run_chunk_00.res`, `run_chunk_01.res`, etc. into a single `run_3_final.res`.

```bash
python drafts/merge_chunks.py
```

### `parameter_tuning_*.py`
Grid search analysis and visualization scripts. Output PNG plots of MAP vs. parameter sweeps.

---

## 📚 References

| Paper / Resource | Relevance |
|-----------------|-----------|
| [Query2Doc — Wang et al., 2023](https://arxiv.org/abs/2303.07678) | LLM-based query expansion |
| [A Bag of Tricks for Cross-Encoders — Pradeep et al., ECIR 2022](https://cs.uwaterloo.ca/~jimmylin/publications/Pradeep_etal_ECIR2022.pdf) | Neural reranking on ROBUST04 |
| [Reciprocal Rank Fusion — Cormack & Clarke, 2009](https://dl.acm.org/doi/10.1145/3596512) | RRF combination method |
| [Pyserini ROBUST04 Experiments](https://github.com/castorini/pyserini/blob/master/docs/experiments-robust04.md) | BM25 / RM3 baselines |
| [ROBUST04 Dataset (Papers with Code)](https://paperswithcode.com/dataset/robust04) | Benchmark description |
| [Hybrid Search Explained — Weaviate](https://weaviate.io/blog/hybrid-search-explained) | Hybrid retrieval best practices |

---

## 🔐 Security Note

API keys (`HF_TOKEN`, `COHERE_API_KEY`, `GROQ_API_KEY`) must **never** be committed to this repository.  
Always load them at runtime from **Colab Secrets** or environment variables:

```python
import os
from google.colab import userdata

HF_TOKEN        = userdata.get('HF_TOKEN')
COHERE_API_KEY  = userdata.get('COHERE_API_KEY')
GROQ_API_KEY    = userdata.get('GROQ_API_KEY')
```

---

*TREC ROBUST04 · Information Retrieval · CS Course Final Project*
