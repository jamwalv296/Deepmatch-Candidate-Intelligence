import sys
import os
import gzip
import json
import heapq
import pandas as pd
from src.engine import DeepMatchEngine

def run():
    matcher = DeepMatchEngine()
    heap = []
    
    with gzip.open("data/candidates.jsonl.gz", "rt", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            cand = json.loads(line)
            evidence = matcher.extract_evidence(cand)
            score, reasoning = matcher.compute_final_score(evidence)
            
            if len(heap) < 100:
                heapq.heappush(heap, (score, cand["candidate_id"], reasoning))
            elif score > heap[0][0]:
                heapq.heapreplace(heap, (score, cand["candidate_id"], reasoning))
    
    res = sorted(heap, key=lambda x: x[0], reverse=True)
    out = [{"candidate_id": c, "rank": i+1, "score": round(s, 4), "reasoning": r} 
           for i, (s, c, r) in enumerate(res)]
    
    pd.DataFrame(out).to_csv("team_submission.csv", index=False)

if __name__ == "__main__":
    run()