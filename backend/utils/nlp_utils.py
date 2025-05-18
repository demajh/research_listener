"""
Utilities for
• downloading the most-recent arXiv papers in a channel
• filtering them against a user’s area-of-interest description
• producing short, citation-ready summaries
-------------------------------------------------------------------
If an OPENAI_API_KEY is set, the code will transparently switch to
embedding-based relevance scoring and GPT-generated summaries.
Otherwise it falls back to lightweight keyword / extractive methods.
"""

import os
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

import numpy as np
import requests
import feedparser

# Optional heavy deps (only import if the key is present)
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    import openai

# ------------------------------------------------------------------
# 1. Fetch new papers
# ------------------------------------------------------------------

ARXIV_API = "https://export.arxiv.org/api/query"


def fetch_latest(channel: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Pull the most-recent `max_results` papers from an arXiv category
    during the last 24 h window (UTC).

    Returns a list of plain-dict records:
        {title, abstract, authors, link, arxiv_id, updated}
    """
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    query = (
        f"search_query=cat:{channel}"
        f"+AND+lastUpdatedDate:[{yesterday}0000+TO+{today}0000]"
        f"&sortBy=lastUpdatedDate&sortOrder=descending&max_results={max_results}"
    )

    resp = requests.get(f"{ARXIV_API}?{query}", timeout=20)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    papers = []
    for entry in feed.entries:
        papers.append(
            {
                "title": entry.title.strip().replace("\n", " "),
                "abstract": re.sub(r"\s+", " ", entry.summary.strip()),
                "authors": [a.name for a in entry.authors],
                "link": entry.link,
                "arxiv_id": entry.id.split("/")[-1],
                "updated": entry.updated,
            }
        )
    return papers


# ------------------------------------------------------------------
# 2. Filtering
# ------------------------------------------------------------------

def _keyword_filter(papers: List[Dict[str, Any]], interest: str) -> List[Dict[str, Any]]:
    """Very simple keyword OR logic (lower-case, whole-word)."""
    tokens = {t.lower() for t in re.findall(r"\w+", interest)}
    keep = []
    for p in papers:
        blob = f"{p['title']} {p['abstract']}".lower()
        if any(tok in blob for tok in tokens):
            keep.append(p)
    return keep


def _embedding_filter(papers: List[Dict[str, Any]], interest: str, k: int = 15,
                      threshold: float = 0.78) -> List[Dict[str, Any]]:
    """Cosine-similarity ranking via OpenAI embeddings."""
    # 1 request for user interest + batch request for papers
    query_emb = openai.Embedding.create(model="text-embedding-3-small", input=[interest])["data"][0]["embedding"]

    # Chunk abstracts to stay within 2048 inputs per call
    abstract_texts = [p["abstract"][:4096] for p in papers]
    paper_embs = openai.Embedding.create(model="text-embedding-3-small", input=abstract_texts)["data"]
    scores = []
    for idx, pdata in enumerate(paper_embs):
        vec = pdata["embedding"]
        sim = np.dot(vec, query_emb) / (np.linalg.norm(vec) * np.linalg.norm(query_emb))
        scores.append((sim, idx))
    # Top-k then threshold
    scores.sort(reverse=True)
    sel = [papers[i] for sim, i in scores[:k] if sim >= threshold]
    return sel


def filter_articles(papers: List[Dict[str, Any]], interest: str) -> List[Dict[str, Any]]:
    """
    Return only the papers relevant to `interest`.
    Chooses embedding or keyword mode automatically.
    """
    if USE_OPENAI:
        try:
            return _embedding_filter(papers, interest)
        except Exception as e:
            # fall back gracefully
            print("Embedding filtering failed – falling back to keywords:", e)
    return _keyword_filter(papers, interest)


# ------------------------------------------------------------------
# 3. Summarisation
# ------------------------------------------------------------------

def _gpt_summary(text: str, max_tokens: int = 160) -> str:
    """Few-shot prompt to boil an abstract to key points + citation."""
    prompt = (
        "You are an expert technical writer.\n"
        "Summarise the core contribution of the following arXiv abstract "
        "in 3 concise bullet points (max ~120 words total). "
        "Focus on what is new and why it matters.\n\nAbstract:\n"
        f"{text}\n\nSummary:"
    )
    chat = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=max_tokens,
    )
    return chat.choices[0].message.content.strip()


def _extractive_summary(text: str, n_sentences: int = 3) -> str:
    """Return the first `n_sentences` sentences of the abstract."""
    sentences = re.split(r"(?<=[\.!?])\s+", text)
    return " ".join(sentences[:n_sentences])


def summarise_article(paper: Dict[str, Any]) -> str:
    """Generate a citation-ready summary markdown block for one paper."""
    abstract = paper["abstract"]
    try:
        summary_body = _gpt_summary(abstract) if USE_OPENAI else _extractive_summary(abstract)
    except Exception as e:
        print("GPT summary failed – falling back to extractive:", e)
        summary_body = _extractive_summary(abstract)

    authors = ", ".join(paper["authors"][:4]) + (" et al." if len(paper["authors"]) > 4 else "")
    updated = datetime.strptime(paper["updated"][:10], "%Y-%m-%d").strftime("%d %b %Y")

    return (
        f"### [{paper['title']}]({paper['link']})  \n"
        f"*{authors}* — *{updated}*  \n"
        f"{summary_body}\n"
    )

