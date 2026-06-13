# 🔍 Text Retrieval & Search Engines — Final Project

<div align="center">

**Reichman University · Efi Arazi School of Computer Science · Semester 1, 2026**

[![Course](https://img.shields.io/badge/Course-Text%20Retrieval%20%26%20Search%20Engines-blue?style=flat-square)](.)
[![Dataset](https://img.shields.io/badge/Dataset-TREC%20ROBUST04-orange?style=flat-square)](https://trec.nist.gov/data/robust.html)
[![Best MAP](https://img.shields.io/badge/Best%20MAP-0.4044-brightgreen?style=flat-square)](.)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=flat-square)](.)

| 👤 Ron Dagani | 👤 Gilad Tsfaty | 👤 Tal Hibner |
|:---:|:---:|:---:|
| Run 1 · LLM Tournament (draft) | Run 2 · LLM Tournament ⭐ | Run 3 · Hybrid RRF |

</div>

---

## 📋 Overview

Ad-hoc document retrieval competition over the **TREC ROBUST04** benchmark — ~528K newswire articles, 249 queries (50 train / 199 test), evaluated by **MAP**.

We submitted three ranked runs across two distinct retrieval strategies, with the Seeded LLM Tournament as our "beyond class material" method — achieving a final MAP of **0.4044** on the 199 test queries.

---

## 📁 Repository Structure

```
.
├── 📂 data/
│   ├── queriesROBUST.txt          # 249 ROBUST04 queries
│   ├── qrels_50_Queries           # Relevance judgments for 50 training queries
│   └── qrels.robust2004.txt       # Full qrels for local evaluation
│
├── 📂 results/
│   ├── run_1.res                  # Ron   — Seeded LLM Tournament (draft)
│   ├── run_2.res                  # Gilad — Seeded LLM Tournament (final · MAP 0.4044)
│   └── run_3.res                  # Tal   — Hybrid Multi-Stage Ranking with RRF
│
├── 📂 drafts/                     # Development notebooks and scripts
│
├── 📄 Final_Part_A_Ranking_Challenge.pdf      # Assignment spec (Part A)
├── 📄 Final_Project_PART_B.pdf               # Assignment spec (Part B)
├── 📄 Final_Project_PART_B-our-solution.pdf  # Written solution (Part B)
└── 📄 seeded_llm_tournament.pdf              # Presentation slides
```

---

## 🏆 Results

| Run | Author | Method | MAP (test) |
|:---:|:------:|--------|:----------:|
| Run 1 | Ron | Seeded LLM Tournament (draft) | — |
| **Run 2** ⭐ | **Gilad** | **Seeded LLM Tournament (final)** | **0.4044** |
| Run 3 | Tal | Hybrid Multi-Stage Ranking with RRF | — |

---

## 🧠 Methods

Two distinct retrieval strategies were implemented. The **Seeded LLM Tournament** is the beyond-class-material entry; the **Hybrid Multi-Stage RRF** pipeline combines techniques taught throughout the course.

---

### Method 1 — Hybrid Multi-Stage Ranking with RRF

> 📓 `drafts/hybrid_multi_stage_ranking_with_RRF_Fusion.ipynb` · **Run 3** (Tal)

A classical-plus-neural pipeline that fuses three complementary retrieval signals using rank-based weighting (Cormack et al., 2009).

**Pipeline:**

```
BM25 + RM3 retrieval (top 1,000)
            ↓
   MonoT5-large reranking
            ↓
  RRF fusion of all signals
            ↓
        run_3.res
```

**Components:**

| Component | Details |
|-----------|---------|
| 🔎 BM25 | k1 = 0.9, b = 0.4 · tuned for MonoT5 synergy |
| 📖 RM3 expansion | fb_docs = 15, fb_terms = 120, original_query_weight = 0.03 |
| 🤖 MonoT5-large | `castorini/monot5-large-msmarco-10k` · 770M parameters |
| 🔀 RRF fusion | k = 10, 3-way equal-weight, depth 1,000 |

**Key findings:**

- 📈 MonoT5-large gave a ~8% MAP gain over MonoT5-base
- 🔇 Low RM3 `original_query_weight` (0.03) maximises recall — the neural reranker handles expansion noise
- ⚙️ RRF k = 10 outperformed the paper's default k = 60 in this 3-way setup
- ❌ Adding SPLADE or Contriever degraded performance (−1.8% to −2.2%) due to signal overlap
- ⏱️ MonoT5-large inference runs ~130 s/query on a Colab T4 GPU

---

### Method 2 — Seeded LLM Tournament ✨ *(beyond class material)*

> 📓 `drafts/seeded_llm_tournament.ipynb` · **Run 1** (Ron, draft) · **Run 2** (Gilad, final — MAP 0.4044)

A five-stage pipeline using **GPT-4o-mini** as a zero-shot listwise relevance judge inside a seeded tournament bracket. Inspired by pairwise and listwise LLM ranking literature (Qin et al., 2023; Sun et al., 2023), this approach moves beyond keyword matching to comparative relevance judgment.

---

#### Stage 1 · 🧹 Data Processing & Weighted Query Construction

Documents are cleaned (Unicode normalisation, HTML stripping, whitespace collapsing). Queries are constructed by triplicating the title field before appending the description:

```
query = title × 3 + description
```

> Triplicating the title boosts TF for BM25 and Query Likelihood, ensuring core intent dominates over verbose description noise.

---

#### Stage 2 · 🔍 Base Retrieval Fusion

| Model | Parameters | Weight |
|-------|-----------|:------:|
| BM25 | k1 = 1.2, b = 0.75 | 0.8 |
| Query Likelihood (Dirichlet) | μ = 1000 | 0.2 |

RM3 expansion (30 terms, top-10 feedback docs) applied here to maximise recall. The **original** (non-expanded) query is retained separately for Stage 3.

---

#### Stage 3 · 📄 Semantic Passage Extraction *(top 300 docs)*

Each document is segmented with a sliding window (150-word size, 75-word stride). A Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) scores every window against the original query — the top-scoring window becomes the document's representative passage for the LLM judge.

> 💡 Using the **original** query — not the RM3-expanded one — for passage scoring gave better extraction precision.

---

#### Stage 4 · 🏟️ Seeded Tournament

```
Judge:   GPT-4o-mini
Mode:    Listwise — batch of 4 documents per call
Scoring: score = 10 × 2^(round − 1)
```

**Round 1 is seeded** — the top base-retrieval document faces the three lowest-ranked candidates. This protects high-precision seeds from early elimination. Rounds 2+ use **random shuffling** to promote semantic diversity among survivors.

```
Round 1 — seeded  (300 docs → 75 winners)
┌─────────────────────────────────────────────┐
│  [Doc   1  vs  Doc 300, 299, 298] → winner  │
│  [Doc   2  vs  Doc 297, 296, 295] → winner  │
│  [Doc   3  vs  Doc 294, 293, 292] → winner  │
│                    ...                       │
└─────────────────────────────────────────────┘

Round 2+ — random shuffle
┌─────────────────────────────────────────────┐
│  75 winners reshuffled → further rounds      │
│  → exponential scoring → final ranking       │
└─────────────────────────────────────────────┘
```

> 🥇 Strategies compared: **Seeded > Leapfrog** (1st vs 100th/200th/300th) **> Random** from Round 1

Tournament scores are min-max normalised before fusion.

---

#### Stage 5 · 🔀 Grand Fusion

```
final_score = 0.85 × LLM_score + 0.15 × base_score
```

Top-300 positions are LLM-driven for high precision; documents outside the tournament window retain their base-retrieval order. The 85/15 split strongly favours tournament winners, with the 15% base component acting as a tie-breaker and recall anchor.

---

## ⚙️ Setup

### Requirements

```bash
pip install pyserini torch transformers sentence-transformers openai
```

> Java 11+ is required by Pyserini. On Colab: `apt-get install -y openjdk-11-jdk`

### ROBUST04 Index

Pyserini downloads the prebuilt index automatically on first use:

```python
from pyserini.search.lucene import LuceneSearcher
from pyserini.index.lucene import IndexReader

searcher = LuceneSearcher.from_prebuilt_index('robust04')
reader   = IndexReader.from_prebuilt_index('robust04')
```

> The index uses Porter stemming and no stopword removal.

### API Key *(Method 2 only)*

```python
from google.colab import userdata
import openai
openai.api_key = userdata.get('OPENAI_API_KEY')
```

---

## 📤 Output Format

All `.res` files use the standard **TREC 6-column format**, returning up to 1,000 documents per query:

```
301 Q0 ZF08-175-870  1  0.9821  run2
301 Q0 ZF08-306-044  2  0.9714  run2
...
```

| Column | Value |
|:------:|-------|
| 1 | Query (topic) number |
| 2 | Unused — always `Q0` |
| 3 | Document ID |
| 4 | Rank (ascending from 1) |
| 5 | Relevance score (descending) |
| 6 | Run tag |

---

## 📚 References

1. Qin, Z. et al. (2023). *Large Language Models are Effective Text Rankers with Pairwise Ranking Prompting.* [arXiv:2306.17563](https://arxiv.org/abs/2306.17563)
2. Sun, W. et al. (2023). *Is ChatGPT Good at Search? Investigation of Large Language Models as Re-Ranking Agents.* [arXiv:2304.09542](https://arxiv.org/abs/2304.09542)
3. Nogueira, R. & Cho, K. (2019). *Passage Re-ranking with BERT.* [arXiv:1901.04085](https://arxiv.org/abs/1901.04085)
4. Cormack, G. V., Clarke, C. L. A., & Buettcher, S. (2009). *Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods.* SIGIR 2009.
