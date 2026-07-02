import json
import heapq
from src.engine import DeepMatchEngine, build_candidate_text

def run_ranking_pipeline(input_path, jd_text=None, top_k=100):
    candidates = []
    texts = []

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            cand = json.loads(line)
            candidates.append(cand)
            texts.append(build_candidate_text(cand))

    matcher = DeepMatchEngine(jd_text=jd_text)
    matcher.fit(texts)
    semantic_scores = matcher.semantic_scores()

    heap = []
    for i, cand in enumerate(candidates):
        evidence = matcher.extract_evidence(cand, texts[i], float(semantic_scores[i]))
        score, reasoning = matcher.compute_final_score(evidence, cand)
        item = (score, cand["candidate_id"], reasoning)

        if len(heap) < top_k:
            heapq.heappush(heap, (score, -_id_key(cand["candidate_id"]), item))
        elif score > heap[0][0]:
            heapq.heapreplace(heap, (score, -_id_key(cand["candidate_id"]), item))

    results = [entry[2] for entry in heap]
    results.sort(key=lambda x: (-x[0], x[1]))
    return results[:top_k]

def _id_key(candidate_id):
    digits = "".join(ch for ch in candidate_id if ch.isdigit())
    return int(digits) if digits else 0
