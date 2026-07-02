# DeepMatch — Redrob AI Candidate Ranking

## Approach
1. **Semantic fit (35%)** — TF-IDF (1-2 gram) cosine similarity between each candidate's profile/skills/career text and the job description, fit once over the full corpus for speed.
2. **Technical evidence (30%)** — coverage of must-have (embeddings, vector DBs, retrieval, eval metrics) and nice-to-have JD terms.
3. **Career evidence (20%)** — years-of-experience fit to the JD's 5-9 yr band + evidence of having shipped production systems (not just listing tools).
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

## Files
- `src/jd_profile.py` — structured JD requirements (must-haves, disqualifiers, preferred locations)
- `src/engine.py` — scoring engine
- `pipeline.py` — streaming load + heap-bounded top-100 selection
- `main.py` — entrypoint
