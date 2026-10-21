import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import os
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_FLAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

"""
research_agent.py
-----------------
Research Agent for the Multi-Agent Financial Analysis System (Milestone 3).

Responsibilities:
1. Multi-part Query Handling:
   - Decomposes user questions into atomic search intents.
   - Extracts target company, fiscal year(s), and financial topics.
2. Grounded Vector Retrieval:
   - Queries ChromaDB ('financial_documents') with semantic search.
   - Filters by company/year metadata if specified.
   - Preserves source provenance (document name, page number, chunk text).
3. Step-by-Step Reasoning (Chain of Thought):
   - Evaluates retrieved evidence per sub-question.
   - Synthesizes findings with strict source citations:
     Format: [Source: <DOC_NAME>, Page <PAGE>]
4. Returns structured analytical response with verified citations.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from sentence_transformers import SentenceTransformer

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(SRC_DIR)
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.chroma_manager import ChromaManager


EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K_RETRIEVAL = 6

KNOWN_COMPANIES = ["AMAZON", "APPLE", "INFOSYS", "MICROSOFT", "REALIANCE", "RELIANCE", "TESLA", "META", "ALPHABET", "GOOGLE", "NVIDIA"]
YEAR_PATTERN = re.compile(r"\b(201\d|202\d)\b")


class ResearchAgent:
    """
    Financial Research Agent providing multi-hop retrieval and cited answers.
    """

    def __init__(self, root_dir: str = ROOT_DIR):
        self.root_dir = os.path.abspath(root_dir)
        self.chroma_dir = os.path.join(self.root_dir, "chroma_db")
        self.output_dir = os.path.join(self.root_dir, "outputs", "research_notes")
        os.makedirs(self.output_dir, exist_ok=True)

        self._embedder: Optional[SentenceTransformer] = None
        self._chroma: Optional[ChromaManager] = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            print(f"[ResearchAgent] Loading embedding model '{EMBEDDING_MODEL}'...")
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedder

    @property
    def chroma(self) -> ChromaManager:
        if self._chroma is None:
            self._chroma = ChromaManager(self.chroma_dir)
        return self._chroma

    def _decompose_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze the query to detect entities (companies, years) and sub-questions.
        """
        q_upper = query.upper()
        detected_companies = []

        # Collect dynamically known companies from ChromaDB + base list
        all_known = set(KNOWN_COMPANIES)
        try:
            stats = self.chroma.get_collection_stats()
            for doc_key in stats.get("documents", {}).keys():
                parts = doc_key.split("_")
                if parts:
                    all_known.add(parts[0].upper())
        except Exception:
            pass

        for comp in all_known:
            if comp in q_upper:
                norm_comp = "REALIANCE" if comp == "RELIANCE" else comp
                if norm_comp not in detected_companies:
                    detected_companies.append(norm_comp)

        detected_years = list(set(YEAR_PATTERN.findall(query)))

        # Split multi-part query by connectors ("and", "also", "?", ";", "vs")
        clauses = re.split(r"(?<=[?.!;])\s+|\s+(?:and also|as well as|additionally)\s+", query, flags=re.IGNORECASE)
        sub_queries = [c.strip() for c in clauses if len(c.strip()) > 5]
        if not sub_queries:
            sub_queries = [query.strip()]

        return {
            "original_query": query,
            "companies": detected_companies,
            "years": detected_years,
            "sub_queries": sub_queries,
        }

    def _retrieve_evidence(
        self,
        sub_query: str,
        company: Optional[str] = None,
        year: Optional[str] = None,
        top_k: int = TOP_K_RETRIEVAL
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search against ChromaDB with optional metadata filters.
        """
        where_filter = None
        filters = []
        if company:
            filters.append({"company": company.upper()})
        if year:
            filters.append({"year": str(year)})

        if len(filters) == 1:
            where_filter = filters[0]
        elif len(filters) > 1:
            where_filter = {"$and": filters}

        q_vec = self.embedder.encode([sub_query], convert_to_numpy=True).tolist()

        try:
            results = self.chroma.query(
                query_embeddings=q_vec,
                n_results=top_k,
                where=where_filter,
            )
        except Exception as e:
            print(f"[ResearchAgent] Query error: {e}")
            return []

        evidence = []
        if not results or not results.get("documents"):
            return evidence

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results.get("distances", [[0] * len(docs)])[0]

        for chunk_text, meta, dist in zip(docs, metas, distances):
            evidence.append({
                "sub_query": sub_query,
                "document": meta.get("doc_name", "UNKNOWN_DOC"),
                "company": meta.get("company", ""),
                "year": meta.get("year", ""),
                "page_number": meta.get("page_number", "N/A"),
                "chunk_index": meta.get("chunk_index", 0),
                "similarity_score": round(1.0 - float(dist), 4) if dist is not None else 1.0,
                "text": chunk_text.strip(),
            })

        return evidence

    def research(self, query: str) -> Dict[str, Any]:
        """
        Execute multi-hop research process for a user query.

        Returns
        -------
        Structured dict with:
        - query
        - decomposition (companies, years, sub_queries)
        - step_by_step_reasoning (analysis trail)
        - answer (synthesis grounded in documents)
        - citations (complete provenance for all referenced facts)
        """
        print(f"\n[ResearchAgent] Processing query: \"{query}\"")
        decomposition = self._decompose_query(query)
        companies = decomposition["companies"]
        years = decomposition["years"]
        sub_queries = decomposition["sub_queries"]

        print(f"[ResearchAgent] Identified companies: {companies or 'All'}, years: {years or 'All'}")
        print(f"[ResearchAgent] Decomposed into {len(sub_queries)} sub-queries.")

        all_evidence: List[Dict[str, Any]] = []
        reasoning_steps: List[str] = []
        citations: List[Dict[str, Any]] = []
        seen_citations = set()

        # Step 1: Retrieval per sub-query and company/year target
        step_idx = 1
        for sq in sub_queries:
            reasoning_steps.append(f"Step {step_idx}: Investigating sub-query '{sq}'...")
            step_idx += 1

            if companies:
                for comp in companies:
                    target_year = years[0] if len(years) == 1 else None
                    ev_items = self._retrieve_evidence(sq, company=comp, year=target_year)
                    all_evidence.extend(ev_items)
            else:
                ev_items = self._retrieve_evidence(sq, company=None, year=years[0] if years else None)
                all_evidence.extend(ev_items)

        # Step 2: Synthesize findings and deduplicate citations
        # Sort evidence by similarity
        all_evidence.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_evidence = all_evidence[:8]

        extracted_findings: List[Dict[str, Any]] = []
        for ev in top_evidence:
            citation_key = (ev["document"], ev["page_number"])
            citation_tag = f"[Source: {ev['document']}, Page {ev['page_number']}]"

            if citation_key not in seen_citations:
                seen_citations.add(citation_key)
                citations.append({
                    "citation_tag": citation_tag,
                    "document": ev["document"],
                    "page_number": ev["page_number"],
                    "company": ev["company"],
                    "year": ev["year"],
                    "similarity": ev["similarity_score"],
                    "excerpt": ev["text"][:280] + ("..." if len(ev["text"]) > 280 else ""),
                })

            # Extract first 2 meaningful sentences
            sentences = [s.strip() for s in ev["text"].replace("\n", " ").split(".") if len(s.strip()) > 20]
            summary_snippet = ". ".join(sentences[:2]) if sentences else ev["text"][:200]

            extracted_findings.append({
                "company": ev["company"],
                "year": ev["year"],
                "finding": summary_snippet,
                "citation": citation_tag,
            })

        reasoning_steps.append(
            f"Step {step_idx}: Retrieved {len(all_evidence)} chunks, prioritized top {len(top_evidence)} "
            f"grounded segments across {len(citations)} unique document sections."
        )

        # Step 3: Format synthesized answer
        answer_lines = []
        answer_lines.append(f"### Research Findings for: \"{query}\"\n")

        if not citations:
            answer_lines.append("No directly matching financial disclosures were found in the indexed documents.")
            answer_text = "\n".join(answer_lines)
        else:
            answer_lines.append("Based on verified disclosures indexed in the financial knowledge base:\n")
            for idx, item in enumerate(extracted_findings[:5], 1):
                clean_finding = item["finding"].strip()
                if not clean_finding.endswith("."):
                    clean_finding += "."
                comp_tag = f"**{item['company']} ({item['year']})**: " if item["company"] else ""
                answer_lines.append(f"{idx}. {comp_tag}{clean_finding} {item['citation']}\n")

            answer_lines.append("#### Source Citations")
            for c in citations:
                answer_lines.append(f"- **{c['citation_tag']}**: \"{c['excerpt']}\"")

            answer_text = "\n".join(answer_lines)

        result = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "query_analysis": decomposition,
            "reasoning_steps": reasoning_steps,
            "answer": answer_text,
            "citations": citations,
            "top_findings": extracted_findings[:5],
            "total_evidence_count": len(all_evidence),
        }

        # Save research note
        sanitized_q = re.sub(r"[^\w\-_\. ]", "", query)[:40].strip().replace(" ", "_")
        out_file = os.path.join(self.output_dir, f"research_{sanitized_q}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[ResearchAgent] Research completed with {len(citations)} source citations. Saved to {out_file}")
        return result


if __name__ == "__main__":
    agent = ResearchAgent(ROOT_DIR)
    q = "What were Amazon's major revenue drivers in 2023 and what antitrust or regulatory risks were noted?"
    res = agent.research(q)
    print("\n" + res["answer"])
