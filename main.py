import sys
import pandas as pd
from pipeline import run_ranking_pipeline

def load_jd_text(path):
    try:
        import docx
        d = docx.Document(path)
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    except Exception:
        return None

def main():
    input_file = "data/candidates.jsonl"
    jd_path = sys.argv[1] if len(sys.argv) > 1 else None
    jd_text = load_jd_text(jd_path) if jd_path else None

    results = run_ranking_pipeline(input_file, jd_text=jd_text)

    rounded = [(round(s, 4), c, r) for s, c, r in results]
    rounded.sort(key=lambda x: (-x[0], x[1]))

    out = [{"candidate_id": c, "rank": i + 1, "score": s, "reasoning": r}
           for i, (s, c, r) in enumerate(rounded)]

    pd.DataFrame(out).to_csv("team_submission.csv", index=False)
    print("Execution Complete: team_submission.csv generated.")

if __name__ == "__main__":
    main()
