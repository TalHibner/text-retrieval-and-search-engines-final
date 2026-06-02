# 🔍 Text Retrieval & Search Engines — Final Project

> **ROBUST04 Ad-Hoc Retrieval Competition** · Semester 1, 2026  
> Three-run IR system combining classical BM25/QL fusion, MonoT5 neural reranking, and a novel **Seeded LLM Tournament** re-ranker — achieving a final MAP of **0.4044** on the test set.

---

## 📑 Table of Contents

- [Project Overview](#-project-overview)
- [The Challenge](#-the-challenge)
- [System Architecture](#-system-architecture)
  - [Run 1 — BM25 + RM3 Baseline](#run-1--bm25--rm3-baseline)
  - [Run 2 — Neural Reranking Pipeline (MonoT5)](#run-2--neural-reranking-pipeline-monot5)
  - [Run 3 — Seeded LLM Tournament ⭐ Best Result](#run-3--seeded-llm-tournament-⭐-best-result)
- [Repository Structure](#-repository-structure)
- [Installation & Setup](#-installation--setup)
- [Configuration Variables](#-configuration-variables)
- [Usage](#-usage)
- [Evaluation](#-evaluation)
- [Results & Findings](#-results--findings)
- [References](#-references)

---

## 📖 Project Overview

This repository contains the final project submission for the **Text Retrieval and Search Engines** course (Semester 1, 2026). The task is an ad-hoc document retrieval competition over the **ROBUST04** collection — ~528,000 newswire articles — evaluated with **249 TREC queries** (50 training, 199 test).

The goal is to maximize **Mean Average Precision (MAP)** by submitting three ranked result lists (runs) of the top-1,000 documents per query in standard TREC format.

> **Team:** Students 208288647, 318170917, 026548446

---

## 🏆 The Challenge

- **Collection:** ROBUST04 (~528K newswire documents), indexed with Porter stemming, no stopword removal
- **Queries:** 249 total — 50 for training/parameter tuning, 199 for blind test evaluation
- **Deliverable:** 3 × `run_i.res` files in TREC 6-column format:

```
<topic_id>  Q0  <doc_id>  <rank>  <score>  <run_tag>
630         Q0  ZF08-175-870   1   0.97   run1
630         Q0  ZF08-306-044   2   0.85   run1
...
```

- **Metric:** MAP on 199 test queries
- **Constraint:** Fully reproducible on Google Colab (free tier + T4 GPU)

---

## 🧠 System Architecture

### Run 1 — BM25 + RM3 Baseline

A strong classical baseline using Pyserini's BM25 with RM3 pseudo-relevance feedback, tuned by grid search on 50 training queries.

**Techniques:**
- BM25 with Porter-stemmed index
- RM3 pseudo-relevance feedback for automatic query expansion
- Grid search over BM25 (`k1`, `b`) and RM3 (`fb_docs`, `fb_terms`, `original_query_weight`) parameters

**Key parameters (after tuning):**
| Parameter | Value | Description |
|-----------|-------|-------------|
| `k1` | 0.9 | BM25 term frequency saturation |
| `b` | 0.4 | BM25 document length normalization |
| `fb_docs` | 10 | RM3 feedback documents |
| `fb_terms` | 10–30 | RM3 expansion terms |
| `original_query_weight` | 0.5 | Weight of original query in RM3 |

---

### Run 2 — Neural Reranking Pipeline (MonoT5)

A two-stage pipeline: BM25+QL hybrid retrieval followed by MonoT5-large neural reranking with 3-way RRF fusion.

**5-Stage Pipeline:**
1. **Data Processing** — Text normalization, HTML stripping, whitespace collapsing, and weighted query construction (title × 3 + description) to boost BM25 TF scores for core intent terms
2. **Hybrid Base Retrieval** — BM25 (80%) + Query Likelihood/Dirichlet (20%) fusion with RM3 expansion (30 terms, 10 feedback docs, `original_query_weight = 0.03`)
3. **MonoT5-large Reranking** — 770M parameter neural cross-encoder reranker on top-100 BM25 candidates
4. **3-way RRF Fusion** — `k=10` (optimized; lower than standard k=60 to emphasize top ranks)
5. **Final Ranking** — Output top-1000 in TREC format

**Key findings:**
- MonoT5-large vs. MonoT5-base: **+8% MAP improvement**
- Very aggressive RM3 (`original_query_weight = 0.03`) is optimal — the neural reranker filters the noise
- Adding SPLADE or Contriever **degraded** performance (−1.8% to −2.2%): overlapping signals, no complementary gain
- MonoT5-large requires ~130s/query on Colab T4 GPU

---

### Run 3 — Seeded LLM Tournament ⭐ Best Result

> **Final MAP on test set: 0.4044**

The signature contribution of this project: a novel **tournament-based LLM re-ranker** using GPT-4o-mini as a zero-shot relevance judge, combined with classical IR for recall stability.

**Motivation:** Moving beyond keyword matching to leverage the comparative reasoning capabilities of LLMs for listwise document ranking, inspired by pairwise ranking prompting literature.

#### 5-Stage Pipeline

**Stage 1 — Data Processing & Query Expansion**
- Aggressive text normalization (Unicode, HTML, whitespace, denoising)
- Weighted query construction: `Title × 3 + Description` → boosts TF-based models
- Reduces index noise by ~15%

**Stage 2 — Base Retrieval Fusion**
- BM25 (`k1=1.2`, `b=0.75`) — primary retriever
- Query Likelihood with Dirichlet smoothing (`μ=1000`) — complementary signal
- RM3 expansion: 30 terms, 10 feedback docs
- Fusion: `Score = 0.8 × BM25 + 0.2 × QL`
- Retrieves top-1,000 candidates (training: top-400, test: top-300 for LLM stage)

**Stage 3 — Semantic Passage Extraction (Cross-Encoder)**
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Sliding window over each document: **150-word windows, 75-word stride**
- Selects the single best window per document for LLM input
- Uses the **original query** (not expanded) for extraction — expansion introduced noise
- Dramatically reduces token usage vs. feeding full documents

**Stage 4 — The Seeded Tournament**
- Judge: `GPT-4o-mini` in listwise mode (batch of 4 documents per match)
- **Round 1 (Seeded):** Top-ranked base documents vs. bottom-ranked (1st vs. 298th, 299th, 300th) — protects high-precision seeds from early elimination
- **Subsequent rounds (Random shuffle):** Encourages semantic diversity
- Scoring formula: `score = Σ 2^(r-1)` where `r` = round reached — exponential points for surviving multiple rounds
- Normalization: Min-Max (divided by max score)

```
Round 1 — 300 docs, seeded bracket
  Match A: [Seed #1  vs. #298, #299, #300]
  Match B: [Seed #2  vs. #297, #296, #295]
  ...
Round 2 — 75 winners, random shuffle
  ...
Final — Champion → Rank #1
```

**Stage 5 — Grand Fusion**
```
Final Score = 0.85 × LLM_Tournament_Score + 0.15 × Base_Retrieval_Score
```
- Top-300 documents: LLM-driven ranking (precision-maximizing)
- Documents 301–1000: retain base score order (stability anchor)

---

## 📁 Repository Structure

```
.
├── Final_Part_A_Ranking_Challenge.pdf    # Assignment spec — Part A (ranking competition)
├── Final_Project_PART_B.pdf             # Assignment spec — Part B (writeup)
├── Final_Project_PART_B-our-solution.pdf # Our submitted Part B writeup
├── seeded_llm_tournament.pdf            # Full technical presentation of Run 3
│
├── data/
│   ├── queriesROBUST.txt                # 249 TREC queries (50 train + 199 test)
│   ├── qrels_50_Queries                 # Relevance judgments for 50 training queries
│   └── qrels.robust2004.txt             # Full qrels (all 249 queries)
│
├── results/
│   ├── run_1.res                        # Run 1 output — BM25 + RM3
│   ├── run_2.res                        # Run 2 output — MonoT5 neural reranking
│   ├── run_3.res                        # Run 3 output — Seeded LLM Tournament
│   ├── 10/                              # Chunked Run 3 results (chunk size 10)
│   └── 30/                              # Chunked Run 3 results (chunk size 30)
│
└── drafts/                              # Development notebooks and utilities
    ├── ROBUST04_Phase1_Fixed.ipynb          # Run 1 implementation
    ├── ROBUST04_Run2_Hybrid_RRF.ipynb       # Run 2 base retrieval
    ├── ROBUST04_Run3_Ensemble.ipynb         # Run 3 ensemble reranking
    ├── ROBUST04_FINAL.ipynb                 # Consolidated final submission notebook
    ├── ROBUST04_FINAL_ULTIMATE.ipynb        # Best optimized pipeline
    ├── GT_Q2D_Data_Gathering.ipynb          # Query2Doc data collection
    ├── GT_Q2D_NoLLM_Advanced_Retrieval.ipynb # Neural reranking without API costs
    ├── evaluate_run.py                      # Standalone MAP evaluation script
    ├── chunked_generation.py                # Fault-tolerant chunked run generation
    ├── merge_chunks.py                      # Merge chunk files into final .res
    └── parameter_tuning_*.py                # Grid search & visualization scripts
```

---

## ⚙️ Installation & Setup

### Environment
The notebooks are designed for **Google Colab** (T4 GPU). For local execution:

```bash
pip install pyserini ir_measures transformers torch sentence-transformers openai
```

> **Java 11+ required** for Pyserini:
> ```bash
> apt-get install openjdk-21-jdk   # Ubuntu/Debian
> ```

### ROBUST04 Index
Pyserini auto-downloads the prebuilt index on first use:

```python
from pyserini.search.lucene import LuceneSearcher
from pyserini.index.lucene import IndexReader

searcher = LuceneSearcher.from_prebuilt_index('robust04')
index_reader = IndexReader.from_prebuilt_index('robust04')
```

> The index was created with **Porter stemming** and **no stopword removal**.

### API Keys (Run 3 only)
Run 3 requires a GPT-4o-mini API key. Set it as a **Colab Secret** or environment variable:

| Variable | Service | Required For |
|----------|---------|-------------|
| `OPENAI_API_KEY` | OpenAI GPT-4o-mini | Tournament judging (Run 3) |
| `HF_TOKEN` | HuggingFace | Private model access (optional) |

> ⚠️ **Never hardcode API keys** in notebooks. Always load from environment:
> ```python
> from google.colab import userdata
> OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
> ```

---

## 🔧 Configuration Variables

### Run 1 — BM25 + RM3

| Variable | Optimized Value | Description |
|----------|----------------|-------------|
| `k1` | `0.9` | BM25 term frequency saturation |
| `b` | `0.4` | BM25 document length normalization |
| `fb_docs` | `10` | RM3 pseudo-relevance feedback documents |
| `fb_terms` | `10–30` | RM3 expansion terms added to query |
| `original_query_weight` | `0.5` | RM3 weight for original query (α) |

### Run 2 — Neural Reranking (MonoT5)

| Variable | Optimized Value | Description |
|----------|----------------|-------------|
| `k1` | `0.9` | BM25 saturation (retuned for MonoT5) |
| `b` | `0.4` | BM25 length norm (retuned for MonoT5) |
| `original_query_weight` | `0.03` | Very aggressive RM3 expansion |
| `reranker_model` | `castorini/monot5-large-msmarco` | 770M param neural reranker |
| `rerank_depth` | `100` | BM25 candidates passed to reranker |
| `rrf_k` | `10` | RRF constant (lower = emphasize top ranks more) |

### Run 3 — Seeded LLM Tournament

| Variable | Value | Description |
|----------|-------|-------------|
| `BM25_WEIGHT` | `0.8` | Base retrieval BM25 contribution |
| `QL_WEIGHT` | `0.2` | Base retrieval Query Likelihood contribution |
| `BM25_k1` | `1.2` | BM25 saturation parameter |
| `BM25_b` | `0.75` | BM25 length normalization |
| `QL_mu` | `1000` | Dirichlet smoothing parameter |
| `RM3_terms` | `30` | Number of RM3 expansion terms |
| `RM3_fb_docs` | `10` | RM3 feedback documents |
| `TITLE_WEIGHT` | `3` | Query title term triplication factor |
| `WINDOW_SIZE` | `150` | Cross-encoder sliding window (words) |
| `WINDOW_STRIDE` | `75` | Sliding window stride (words) |
| `RERANK_DEPTH` | `300` | Documents entering the tournament |
| `BATCH_SIZE` | `4` | Documents per LLM judge match |
| `LLM_WEIGHT` | `0.85` | Final fusion weight for LLM tournament score |
| `BASE_WEIGHT` | `0.15` | Final fusion weight for base retrieval score |
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM judge model |

---

## 🚀 Usage

### Run 1 — BM25 + RM3

```python
from pyserini.search.lucene import LuceneSearcher

searcher = LuceneSearcher.from_prebuilt_index('robust04')
searcher.set_bm25(k1=0.9, b=0.4)
searcher.set_rm3(fb_docs=10, fb_terms=10, original_query_weight=0.5)

results = searcher.search("hubble telescope achievements", k=1000)

# Write TREC output
with open("run_1.res", "w") as f:
    for rank, hit in enumerate(results, 1):
        f.write(f"301 Q0 {hit.docid} {rank} {hit.score:.6f} run1\n")
```

---

### Run 2 — Neural Reranking (MonoT5)

```python
# Stage 1: BM25+QL hybrid retrieval
bm25_results = bm25_searcher.search(query, k=1000)
ql_results   = ql_searcher.search(query, k=1000)
base_results = rrf_fusion([bm25_results, ql_results], k=10)

# Stage 2: MonoT5-large reranking on top-100
from transformers import T5ForConditionalGeneration, T5Tokenizer
reranked = monot5_rerank(query, base_results[:100])

# Stage 3: Final RRF fusion
final = rrf_fusion([reranked, base_results], k=10)
```

---

### Run 3 — Seeded LLM Tournament

```python
# Stage 1: Weighted query construction
query_weighted = (title + " ") * 3 + description

# Stage 2: Base retrieval (BM25 80% + QL 20%)
candidates = hybrid_retrieve(query_weighted, depth=300)

# Stage 3: Passage extraction via Cross-Encoder sliding window
passages = extract_best_passages(
    query_original, candidates,
    window_size=150, stride=75,
    model="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Stage 4: Seeded tournament
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

tournament_scores = run_seeded_tournament(
    query=query_original,
    passages=passages,
    model="gpt-4o-mini",
    batch_size=4
)

# Stage 5: Grand fusion
final_score = 0.85 * tournament_scores + 0.15 * base_scores
```

**Scoring formula:**
```
Tournament score = Σ 2^(round - 1)   for each round a document survives
Final score      = 0.85 × LLM_score_normalized + 0.15 × base_score_normalized
```

---

### Evaluation Script

```bash
cd data/
python ../drafts/evaluate_run.py ../results/run_3.res
```

```
============================================================
📊 RESULTS
============================================================
  MAP:       0.4044  ← Main metric
  P@10:      0.5120
  P@20:      0.4380
  Queries:   199
============================================================
📈 Performance Assessment:
  🌟 EXCELLENT! Top-tier performance!
============================================================
```

### Fault-Tolerant Chunked Generation

For long runs on Colab (to survive disconnects):

```python
# In drafts/chunked_generation.py:
CHUNK_SIZE  = 30   # queries per chunk
START_CHUNK = 0    # resume from this chunk (increment after disconnection)
OUTPUT_DIR  = "."
```

Then merge all chunks:
```bash
python drafts/merge_chunks.py
```

---

## 📊 Results & Findings

### Performance Summary

| Run | Strategy | MAP (test) | vs. BM25 baseline |
|-----|----------|-----------|-------------------|
| BM25 baseline | Standard BM25 | ~0.253 | — |
| **Run 1** | BM25 + RM3 (tuned) | ~0.27 | +7% |
| **Run 2** | MonoT5-large + RRF | ~0.31 | +23% |
| **Run 3** | Seeded LLM Tournament | **0.4044** | **+60%** |

### Key Insights

| Finding | Detail |
|---------|--------|
| **Aggressive RM3 works with neural rerankers** | `original_query_weight = 0.03` (very aggressive) is optimal because MonoT5 filters the expansion noise |
| **MonoT5-large >> MonoT5-base** | +8% MAP improvement from scaling to 770M params |
| **Seeded bracket protects precision** | Seeding round 1 prevents high-quality BM25 documents from early tournament elimination |
| **SPLADE/Contriever hurt performance** | −1.8% to −2.2% — signals overlapped with existing pipeline, adding noise not complementary info |
| **RRF k=10 > k=60** | Lower k emphasizes top-ranked documents more aggressively; optimal for this 3-way fusion setup |
| **LLM token efficiency via passage extraction** | Sliding window (150 words, 75-word stride) with Cross-Encoder selection dramatically reduces GPT-4o-mini token usage |
| **Original query best for passage extraction** | Expanded queries during passage extraction introduced noise — use original query for the Cross-Encoder |

---

## 📚 References

| Paper | Relevance to this project |
|-------|--------------------------|
| Qin et al. (2023). [Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting](https://arxiv.org/abs/2306.17563) | Inspiration for LLM comparative judging in Run 3 |
| Sun et al. (2023). [Is ChatGPT Good at Search? LLMs as Re-Ranking Agents](https://arxiv.org/abs/2304.09542) | Listwise ranking with LLMs; token limit trade-offs addressed by our sliding window |
| Nogueira & Cho (2019). [Passage Re-ranking with BERT](https://arxiv.org/abs/1901.04085) | Basis for Cross-Encoder passage extraction in Stage 3 |
| Nogueira et al. (2020). [Document Ranking with a Pretrained Sequence-to-Sequence Model (MonoT5)](https://arxiv.org/abs/2003.06713) | MonoT5 reranking in Run 2 |
| [Pyserini ROBUST04 Experiments](https://github.com/castorini/pyserini/blob/master/docs/experiments-robust04.md) | BM25/RM3 baseline and parameter guidance |
| Cormack & Clarke (2009). Reciprocal Rank Fusion | RRF fusion formula used in Run 2 |

---

## 🔐 Security Note

API keys (`OPENAI_API_KEY`, `HF_TOKEN`) must **never** be committed to this repository. Always load from runtime secrets:

```python
from google.colab import userdata
import os

OPENAI_API_KEY = userdata.get('OPENAI_API_KEY')
# or locally:
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
```

---

*Text Retrieval and Search Engines · Final Project · Semester 1, 2026*
