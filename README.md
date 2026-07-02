# DeepMatch — Explainable Candidate Ranking Engine
DeepMatch ranks candidates using semantic retrieval, evidence fusion, and recruiter-aware validation instead of traditional keyword matching.

## Ranking Pipeline
1. **Semantic fit (35%)** — TF–IDF (1–2 gram) vectorization over the complete candidate corpus followed by batched cosine similarity against the Job Description.
2. **Technical evidence (30%)** — Benchmarks demonstrated technical evidence against must-have and preferred competencies extracted from the Job Description.
3. **Career evidence (20%)** — Evaluates production ownership, engineering progression, and experience alignment in addition to years-of-experience fit.
4. **Recruitability (15%)** — recruiter response rate, activity recency, notice period, location fit, open-to-work flag.
5. **Gates (multiplicative, not additive)**:
   - Hard disqualifier gate: research-only backgrounds, consulting-only history, CV/speech/robotics without NLP, architecture/lead roles without recent coding, LangChain-only "AI experience".
   - Narrative confidence gate: flags candidates whose title/skills claims aren't backed by career-history evidence (keyword stuffing).

Final score = weighted base score × disqualifier gate × narrative gate.

## Run
```
pip install -r requirements.txt
python main.py path/to/job_description.docx
```
Outputs `team_submission.csv` (candidate_id, rank, score, reasoning), validated against `validate_submission.py`.

## Project Structure
- `src/jd_profile.py` — structured JD requirements (must-haves, disqualifiers, preferred locations)
- `src/engine.py` — scoring engine
- `pipeline.py` — streaming load + heap-bounded top-100 selection
- `main.py` — entrypoint
