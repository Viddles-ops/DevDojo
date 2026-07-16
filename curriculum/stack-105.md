# RAG anatomy: how jAIme finds the right study

RAG = the LLM answers from *retrieved documents*, not memory. jAIme
(pemf_bot_v2) is your fullest implementation — every stage lives in a named
module, so you can read the whole pipeline top to bottom.

## Index time (`ingest.py` → `ingestion/`, `rag/index_store.py`)

1. **Chunking** (`ingestion/chunker.py`): studies are split into ~350-word
   chunks with 60 words of overlap (`CHUNK_MAX_WORDS`/`CHUNK_OVERLAP` in
   config.py). Overlap matters — a sentence cut in half at a boundary would
   otherwise be findable from neither side. Each `Chunk` carries metadata:
   source file, position, sentiment, study type (regex-detected: RCT /
   controlled / observational / review), year.
2. **Embedding** (`ingestion/embedder.py`): each chunk's text becomes a
   384-dim vector via `all-MiniLM-L6-v2` (SBERT) — a *local* model, so
   indexing costs nothing and leaves the machine.
3. **Storage** (`rag/index_store.py`): three files in `index/` — a NumPy
   matrix (`embeddings.npy`), a parallel metadata list (`chunk_meta.json`),
   and a SQLite manifest (`manifest.db`). Ingestion is **incremental**: each
   file's MD5 is checked against the manifest; unchanged files are skipped.

## Query time (`rag/retriever.py` — the interesting part)

1. Embed the question with the same model (must match, or the vectors live
   in different spaces).
2. Cosine similarity against the whole matrix — the cheap first cut.
3. **Sentiment filter by user mode**: reps see only positive/mixed studies;
   clinician mode sees everything. Retrieval is where the access policy
   lives, not the prompt.
4. **MMR** (Maximal Marginal Relevance, `MMR_LAMBDA=0.7`): picks chunks that
   are relevant *and* different from each other — `λ·relevance −
   (1−λ)·similarity-to-already-picked`. Pure top-k would return six
   near-copies of the same best paragraph.
5. **Quality rerank**: RCT > controlled > observational > review, plus
   keyword boosts (human/clinical terms) and demotions (rat, in vitro).
6. **Dedupe** to one chunk per source file; the best `MAX_CONTEXT_CHUNKS=6`
   go into the prompt.

The design lesson: relevance (embeddings) is only stage one — *policy*
(sentiment mode), *diversity* (MMR), and *domain quality* (study rank) are
plain Python you control completely.

## Try it

Open `rag/retriever.py` and read `_mmr()` — set `lam` to 1.0 in your head
and confirm the formula degenerates to plain top-k. Then check `config.py`:
which env var would you change to send more chunks to the LLM, and what's
the trade-off?

## Quiz

1. Why do chunks overlap by 60 words instead of splitting cleanly?
2. What would go wrong if queries were embedded with a different model than
   the chunks were?
3. In MMR, what does λ=0.7 balance, and what failure mode does it prevent
   compared to plain top-k retrieval?
