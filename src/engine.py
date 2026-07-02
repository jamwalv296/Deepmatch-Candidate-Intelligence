import re
from datetime import date
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src import jd_profile as jd


def build_candidate_text(candidate):
    profile = candidate.get("profile", {}) or {}
    history = candidate.get("career_history", []) or []
    skills = candidate.get("skills", []) or []
    skill_names = " ".join(str(s.get("name", "")) for s in skills)
    history_text = " ".join(
        f"{h.get('title','')} {h.get('description','')}" for h in history
    )
    return " ".join([
        str(profile.get("headline", "")),
        str(profile.get("summary", "")),
        str(profile.get("current_title", "")),
        skill_names,
        history_text,
    ]).lower()


def count_hits(text, terms):
    return sum(1 for t in terms if t in text)


class DeepMatchEngine:
    def __init__(self, jd_text=None):
        self.jd_text = (jd_text or jd.JD_TEXT).lower()
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), min_df=2, max_df=0.9, sublinear_tf=True
        )

    def fit(self, candidate_texts):
        corpus = candidate_texts + [self.jd_text]
        matrix = self.vectorizer.fit_transform(corpus)
        self.jd_vector = matrix[-1]
        self.candidate_matrix = matrix[:-1]

    def semantic_scores(self):
        sims = cosine_similarity(self.candidate_matrix, self.jd_vector).ravel()
        max_sim = sims.max() if sims.size else 1.0
        if max_sim <= 0:
            return sims
        return sims / max_sim

    def narrative_gate(self, candidate, text):
        profile = candidate.get("profile", {}) or {}
        title = str(profile.get("current_title", "")).lower()
        is_non_tech_title = any(t in title for t in jd.NON_TECH_TITLE_TERMS)
        is_core_tech_title = any(t in title for t in jd.CORE_TECH_TITLE_TERMS)
        skill_names = " ".join(
            str(s.get("name", "")).lower() for s in candidate.get("skills", []) or []
        )
        history = candidate.get("career_history", []) or []
        history_text = " ".join(h.get("description", "") for h in history).lower()

        claimed_ai = count_hits(skill_names, jd.MUST_HAVE_TERMS + jd.NICE_TO_HAVE_TERMS)
        demonstrated_ai = count_hits(history_text, jd.PROD_SHIP_TERMS) + \
            count_hits(history_text, jd.MUST_HAVE_TERMS)

        if is_non_tech_title and not is_core_tech_title and claimed_ai >= 3 and demonstrated_ai == 0:
            return 0.15, "title/skill mismatch flagged (keyword stuffing risk)"
        if is_non_tech_title and not is_core_tech_title and claimed_ai >= 1:
            return 0.6, "non-technical title with some AI skill claims; discounted"
        return 1.0, "title and career narrative are internally consistent"

    def hard_disqualifiers(self, candidate, text):
        profile = candidate.get("profile", {}) or {}
        history = candidate.get("career_history", []) or []
        title = str(profile.get("current_title", "")).lower()
        current_company = str(profile.get("current_company", "")).lower()
        history_text = " ".join(h.get("description", "") for h in history).lower()
        companies = [str(h.get("company", "")).lower() for h in history] + [current_company]

        reasons = []
        gate = 1.0

        if any(t in text for t in jd.RESEARCH_ONLY_TERMS) and not any(t in text for t in jd.PROD_SHIP_TERMS):
            gate *= 0.2
            reasons.append("research-only background, no production deployment evidence")

        if companies and all(c in jd.CONSULTING_FIRMS for c in companies if c):
            gate *= 0.3
            reasons.append("consulting-only career history (no product company experience)")

        cv_hits = count_hits(text, jd.CV_SPEECH_ROBOTICS_TERMS)
        nlp_hits = count_hits(text, jd.NLP_IR_TERMS)
        if cv_hits > 0 and nlp_hits == 0:
            gate *= 0.4
            reasons.append("CV/speech/robotics background without NLP/IR exposure")

        if any(t in text for t in jd.TECH_LEAD_ARCHITECT_TERMS) and "engineer" not in title:
            gate *= 0.7
            reasons.append("moved into architecture/lead role, limited recent hands-on coding signal")

        if any(t in history_text for t in jd.LANGCHAIN_ONLY_TERMS) and \
           not any(t in history_text for t in jd.PRE_LLM_TERMS):
            gate *= 0.5
            reasons.append("AI experience limited to recent LangChain/LLM wrapper work")

        return gate, reasons

    def career_evidence(self, candidate, text):
        profile = candidate.get("profile", {}) or {}
        yoe = float(profile.get("years_of_experience", 0) or 0)
        yoe_fit = 1.0 - min(1.0, abs(yoe - 7) / 9)
        ship_hits = count_hits(text, jd.PROD_SHIP_TERMS)
        ship_score = min(1.0, ship_hits / 3)
        score = 0.5 * yoe_fit + 0.5 * ship_score
        label = "strong shipped-system evidence" if ship_score > 0.6 else "limited evidence of shipping production systems"
        return score, f"{yoe:.1f} yrs experience ({label})"

    def technical_evidence(self, text):
        must_hits = count_hits(text, jd.MUST_HAVE_TERMS)
        nice_hits = count_hits(text, jd.NICE_TO_HAVE_TERMS)
        score = min(1.0, (must_hits / 6) * 0.8 + (nice_hits / 8) * 0.2)
        label = "strong technical alignment with core requirements" if score > 0.6 \
            else "partial alignment with core technical requirements"
        return score, f"{must_hits} core / {nice_hits} nice-to-have skill signals ({label})"

    def recruitability(self, candidate):
        signals = candidate.get("redrob_signals", {}) or {}
        profile = candidate.get("profile", {}) or {}

        resp = float(signals.get("recruiter_response_rate", 0.0) or 0.0)
        open_flag = 1.0 if signals.get("open_to_work_flag") else 0.5

        last_active = signals.get("last_active_date")
        recency = 0.5
        if last_active:
            try:
                y, m, d = [int(x) for x in last_active.split("-")]
                days = (date(2026, 7, 2) - date(y, m, d)).days
                recency = max(0.0, 1.0 - days / 180)
            except Exception:
                pass

        notice = signals.get("notice_period_days", 60) or 60
        notice_score = 1.0 if notice <= 30 else max(0.3, 1.0 - (notice - 30) / 90)

        location = str(profile.get("location", "")).lower()
        willing = bool(signals.get("willing_to_relocate", False))
        loc_ok = any(p in location for p in jd.PREFERRED_LOCATIONS)
        location_score = 1.0 if loc_ok else (0.6 if willing else 0.2)

        score = 0.35 * resp + 0.2 * recency + 0.15 * notice_score + 0.15 * location_score + 0.15 * open_flag
        label = "strong recruiter responsiveness and availability" if score > 0.6 \
            else "weak availability/responsiveness signals; down-weighted"
        return min(1.0, score), f"response rate {resp:.2f}, {label}"

    def extract_evidence(self, candidate, text, semantic_score):
        gate, disqualifier_reasons = self.hard_disqualifiers(candidate, text)
        n_gate, narrative_reason = self.narrative_gate(candidate, text)
        career_score, career_text = self.career_evidence(candidate, text)
        tech_score, tech_text = self.technical_evidence(text)
        rec_score, rec_text = self.recruitability(candidate)

        return {
            "semantic": semantic_score,
            "technical": {"score": tech_score, "text": tech_text},
            "career": {"score": career_score, "text": career_text},
            "recruitability": {"score": rec_score, "text": rec_text},
            "gate": gate,
            "narrative_gate": n_gate,
            "reasons": disqualifier_reasons,
            "narrative_reason": narrative_reason,
        }

    def compute_final_score(self, evidence, candidate):
        profile = candidate.get("profile", {}) or {}
        base = (
            0.35 * evidence["semantic"]
            + 0.30 * evidence["technical"]["score"]
            + 0.20 * evidence["career"]["score"]
            + 0.15 * evidence["recruitability"]["score"]
        )
        final_score = base * evidence["gate"] * evidence["narrative_gate"]

        title = profile.get("current_title", "Candidate")
        yoe = profile.get("years_of_experience", 0)
        summary_bits = [
            f"{title} with {yoe} yrs.",
            evidence["technical"]["text"] + ".",
            evidence["career"]["text"] + ".",
            evidence["recruitability"]["text"] + ".",
        ]
        if evidence["reasons"]:
            summary_bits.append("Concerns: " + "; ".join(evidence["reasons"]) + ".")
        if evidence["narrative_gate"] < 1.0:
            summary_bits.append(evidence["narrative_reason"] + ".")

        reasoning = " ".join(summary_bits)
        return final_score, reasoning
