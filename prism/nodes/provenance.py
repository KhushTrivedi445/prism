import re
from typing import List, Dict, Any
from prism.state import PRISMState

def _split_into_sentences(text: str) -> List[str]:
    if not text:
        return []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    statements = []
    for line in lines:
        if line.startswith("#") or line.startswith("-") or line.startswith("*"):
            clean_line = re.sub(r"^[#\-\*\d\.\s]+", "", line).strip()
            if clean_line:
                statements.append(clean_line)
        else:
            sents = re.split(r"(?<=[.!?])\s+", line)
            for s in sents:
                s_clean = s.strip()
                if len(s_clean) > 10:
                    statements.append(s_clean)
    return statements

def provenance_node(state: PRISMState) -> dict:
    fact_graph = state.get("fact_graph", {})
    claims = fact_graph.get("claims", [])
    metrics = fact_graph.get("metrics", [])
    recommendations = fact_graph.get("recommendations", [])
    dates = fact_graph.get("dates", [])
    synopsis = fact_graph.get("synopsis", "")

    # Compile fact bank
    fact_bank = []
    for c in claims:
        fact_bank.append({
            "claim_text": c.get("text", ""),
            "source_span": c.get("source_span", ""),
            "confidence": c.get("confidence", 0.95),
            "type": "claim"
        })
    for m in metrics:
        fact_bank.append({
            "claim_text": f"{m.get('name')}: {m.get('value')} ({m.get('context')})",
            "source_span": m.get("source_span", ""),
            "confidence": 0.98,
            "type": "metric"
        })
    for r in recommendations:
        fact_bank.append({
            "claim_text": r.get("text", ""),
            "source_span": r.get("source_span", ""),
            "confidence": 0.90,
            "type": "recommendation"
        })
    for d in dates:
        fact_bank.append({
            "claim_text": f"{d.get('date')} - {d.get('event')}",
            "source_span": d.get("source_span", ""),
            "confidence": 0.95,
            "type": "date"
        })

    if not fact_bank and synopsis:
        fact_bank.append({
            "claim_text": synopsis,
            "source_span": synopsis,
            "confidence": 0.85,
            "type": "synopsis"
        })

    provenance_records: List[Dict[str, Any]] = []
    selected_outputs = state.get("selected_outputs", [])

    for channel in selected_outputs:
        content = ""
        if channel == "linkedin":
            content = state.get("linkedin_output", "")
        elif channel == "twitter":
            content = state.get("twitter_output", "")
        elif channel == "summary":
            content = state.get("summary_output", "")
        elif channel == "advisory":
            content = state.get("advisory_output", "")
        elif channel == "presentation":
            pres = state.get("presentation_output", {})
            if isinstance(pres, dict):
                bullets = []
                for s in pres.get("slides", []):
                    bullets.append(f"Slide: {s.get('title', '')}")
                    bullets.extend(s.get("content", []))
                content = "\n".join(bullets)

        if not content:
            continue

        statements = _split_into_sentences(content)

        for stmt in statements:
            best_fact = None
            best_score = -1

            stmt_words = set(re.findall(r"\w+", stmt.lower()))

            for fact in fact_bank:
                fact_words = set(re.findall(r"\w+", (fact["claim_text"] + " " + fact["source_span"]).lower()))
                common = stmt_words.intersection(fact_words)
                score = len(common) / (len(stmt_words) + 1e-5)

                if score > best_score:
                    best_score = score
                    best_fact = fact

            if best_fact and best_score > 0.15:
                provenance_records.append({
                    "output_channel": channel,
                    "output_statement": stmt,
                    "claim_text": best_fact["claim_text"],
                    "source_span": best_fact["source_span"],
                    "confidence": round(min(0.99, max(0.70, best_fact["confidence"] * (0.8 + best_score * 0.2))), 2)
                })
            elif fact_bank:
                top_fact = fact_bank[0]
                provenance_records.append({
                    "output_channel": channel,
                    "output_statement": stmt,
                    "claim_text": top_fact["claim_text"],
                    "source_span": top_fact["source_span"],
                    "confidence": 0.85
                })

    return {"provenance": provenance_records}
