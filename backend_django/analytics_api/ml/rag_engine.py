import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .rag_knowledge_base import FINANCIAL_KNOWLEDGE_CORPUS


class FinancialRAGEngine:
    """
    Vector Retrieval-Augmented Generation (RAG) Engine for Mutual Fund Compliance,
    Scheme Information Documents (SID), SEBI Regulations, and Risk Policies.
    """
    def __init__(self):
        self.chunks = []
        self.doc_metadata = []
        self.vectorizer = None
        self.vector_matrix = None
        self._build_index()

    def _build_index(self):
        """
        Chunks the knowledge base into semantic units and indexes them with dense TF-IDF vectors.
        """
        chunks_list = []
        metadata_list = []

        for doc in FINANCIAL_KNOWLEDGE_CORPUS:
            raw_content = doc["content"].strip()
            # Split by numbered items or double newlines into semantic passages
            paragraphs = [p.strip() for p in raw_content.split('\n') if len(p.strip()) > 25]
            
            for p_idx, para in enumerate(paragraphs):
                chunks_list.append(para)
                metadata_list.append({
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "chunk_index": p_idx,
                    "text": para
                })

        self.chunks = chunks_list
        self.doc_metadata = metadata_list
        
        # Fit vectorizer with unigram and bigram features and sublinear term frequency scaling
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words='english')
        self.vector_matrix = self.vectorizer.fit_transform(self.chunks)
        print(f"[RAG ENGINE] Indexed {len(self.chunks)} semantic knowledge chunks across {len(FINANCIAL_KNOWLEDGE_CORPUS)} regulatory documents.")

    def retrieve(self, query, top_k=3, min_score=0.08):
        """
        Retrieves top-k most semantically relevant knowledge chunks for a query.
        """
        if not query or self.vector_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.vector_matrix).flatten()
        top_indices = np.argsort(similarities)[::-1]

        results = []
        for idx in top_indices[:top_k]:
            score = float(similarities[idx])
            if score >= min_score or len(results) == 0:
                meta = self.doc_metadata[idx]
                results.append({
                    "score": round(score, 4),
                    "doc_id": meta["doc_id"],
                    "title": meta["title"],
                    "category": meta["category"],
                    "text": meta["text"]
                })

        return results

    def format_retrieved_context(self, retrieved_chunks):
        """
        Formats retrieved passages into citation blocks for prompt grounding.
        """
        if not retrieved_chunks:
            return ""

        context_lines = ["\n--- AUTHORITATIVE REGULATORY & SCHEME KNOWLEDGE BASE (RAG CITATIONS) ---"]
        for idx, chunk in enumerate(retrieved_chunks, 1):
            context_lines.append(f"[{idx}] [Source: {chunk['doc_id']} | {chunk['title']}]")
            context_lines.append(f"    Excerpt: {chunk['text']}\n")
        context_lines.append("----------------------------------------------------------------------")
        return "\n".join(context_lines)

    def answer_with_rag(self, query, live_context=None, top_k=3):
        """
        Executes full RAG pipeline: retrieves relevant facts and generates grounded financial guidance with citations.
        """
        retrieved = self.retrieve(query, top_k=top_k)
        rag_context_str = self.format_retrieved_context(retrieved)
        
        citations = [
            {"doc_id": r["doc_id"], "title": r["title"], "score": r["score"]}
            for r in retrieved
        ]

        return {
            "query": query,
            "retrieved_chunks": retrieved,
            "rag_context": rag_context_str,
            "citations": citations
        }


# Global singleton RAG instance
_RAG_ENGINE = None

def get_rag_engine():
    global _RAG_ENGINE
    if _RAG_ENGINE is None:
        _RAG_ENGINE = FinancialRAGEngine()
    return _RAG_ENGINE
