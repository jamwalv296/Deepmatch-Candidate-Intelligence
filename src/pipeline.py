import json
import csv
from src.engine import DeepMatchEngine

class DeepMatchPipeline:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        self.engine = DeepMatchEngine()

    def run(self):
        candidates_scored = []
        with open(self.data_path, "rt", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                candidate = json.loads(line)
                score, reasoning = self.engine.evaluate_candidate(candidate)
                
                candidates_scored.append({
                    "candidate_id": candidate.get("candidate_id"),
                    "score": score,
                    "reasoning": reasoning
                })

        candidates_scored.sort(key=lambda x: x["candidate_id"])
        candidates_scored.sort(key=lambda x: x["score"], reverse=True)
        
        top_100 = candidates_scored[:100]

        with open(self.output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            for idx, cand in enumerate(top_100):
                writer.writerow([
                    cand["candidate_id"],
                    idx + 1,
                    f"{cand['score']:.4f}",
                    cand["reasoning"]
                ])