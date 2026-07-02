import datetime
import re

class DeepMatchEngine:
    def __init__(self):
        self.consulting_firms = {
            "tcs", "tata consultancy", "infosys", "wipro", "accenture", 
            "cognizant", "capgemini", "hcl", "tech mahindra", "ibm"
        }
        
        self.ir_nlp_keywords = {
            "retrieval", "ranking", "search", "recommendation", "embeddings", 
            "vector", "hybrid search", "bm25", "nlp", "information retrieval",
            "pinecone", "weaviate", "qdrant", "milvus", "opensearch", 
            "elasticsearch", "faiss", "ndcg", "mrr", "map", "sentence-transformers"
        }
        
        self.disallowed_domains = {"computer vision", "speech recognition", "robotics", "image segmentation"}

    def evaluate_candidate(self, candidate):
        """
        Evaluates a candidate profile against the Senior AI Engineer (Founding Team) role.
        Returns: (score: float, reasoning: str)
        """
        score = 50.0 
        reasons = []
        
        signals = candidate.get("redrob_signals", {})
        experience_list = candidate.get("experience", [])
        skills = [s.lower() for s in candidate.get("skills", [])]
        
      
        total_months = 0
        product_company_months = 0
        only_consulting = True
        has_product_exp = False
        title_changes = 0
        
        has_shipped_ranking_system = False
        has_pure_research = True
        has_recent_coding = False
        
        current_date = datetime.date(2026, 7, 2)
        
        for idx, exp in enumerate(experience_list):
            company = exp.get("company", "").lower()
            title = exp.get("title", "").lower()
            desc = exp.get("description", "").lower()
            months = exp.get("duration_months", 0)
            total_months += months
            
            is_consulting = any(firm in company for firm in self.consulting_firms)
            if not is_consulting:
                only_consulting = False
                has_product_exp = True
                product_company_months += months
            
            if idx > 0:
                title_changes += 1
                
            if any(kw in desc or kw in title for kw in ["ranking", "search engine", "recommendation system", "retrieval system"]):
                has_shipped_ranking_system = True
                
            if any(kw in desc for kw in ["production", "deployed", "scaled", "kubernetes", "aws", "ci/cd", "pipeline"]):
                has_pure_research = False
                
            if idx == 0 and months >= 18:
                if not any(kw in title for kw in ["architect", "manager", "director", "vp", "lead"]):
                    has_recent_coding = True
                elif any(kw in desc for kw in ["code", "python", "built", "implemented", "shipped"]):
                    has_recent_coding = True
            elif idx == 0 and months < 18:
                has_recent_coding = True

        total_years = total_months / 12.0
        
        if has_pure_research and len(experience_list) > 0:
            score -= 30
            reasons.append("Disqualifier: Career history trends toward pure research without clear production deployment.")
            
        if only_consulting and len(experience_list) > 0:
            score -= 25
            reasons.append("Disqualifier: Candidate history is entirely within IT consulting/service environments.")
            
        if not has_recent_coding and total_years > 5:
            score -= 20
            reasons.append("Disqualifier: Role footprint tracks as pure architecture/management without active coding indicator.")

        if 5.0 <= total_years <= 9.0:
            score += 15
            reasons.append(f"Optimal total experience range ({total_years:.1f} years).")
        elif 6.0 <= total_years <= 8.0:
            score += 20
            reasons.append(f"Ideal core career experience range ({total_years:.1f} years).")
        else:
            score -= 5

        if total_years > 0 and (title_changes / (total_years + 1.0)) > 0.7:
            score -= 15
            reasons.append("Down-weighted: Job transitions or title progressions suggest short-tenure hopping.")

        skills_text = " ".join(skills)
        desc_text = " ".join([exp.get("description", "").lower() for exp in experience_list])
        
        ir_matches = sum(1 for kw in self.ir_nlp_keywords if kw in desc_text or kw in skills_text)
        disallowed_matches = sum(1 for kw in self.disallowed_domains if kw in skills_text or kw in desc_text)
        
        if "langchain" in skills_text and ir_matches < 2:
            score -= 15
            reasons.append("Down-weighted: Profile displays framework proficiency without foundational retrieval/ranking depth.")
            
        if has_shipped_ranking_system:
            score += 20
            reasons.append("Strong Signal: Demonstrated history building or shipping end-to-end ranking/search/recommendation systems.")
            
        if disallowed_matches > 3 and ir_matches < 2:
            score -= 15
            reasons.append("Poor Fit: Focus trends strictly toward computer vision, speech, or robotics over IR/NLP.")

       
        response_rate = signals.get("recruiter_response_rate", 1.0)
        if response_rate < 0.15:
            score -= 20
            reasons.append(f"Critically low recruiter engagement responsiveness ({response_rate * 100:.1f}%).")
        elif response_rate > 0.70:
            score += 10
            reasons.append("High platform availability and recruiter responsiveness interaction.")

        last_active_str = signals.get("last_active_date", "")
        if last_active_str:
            try:
                last_active = datetime.datetime.strptime(last_active_str, "%Y-%m-%d").date()
                days_inactive = (current_date - last_active).days
                if days_inactive > 180:
                    score -= 25
                    reasons.append(f"Inactive for {days_inactive} days; candidate is effectively unavailable.")
                elif days_inactive <= 30:
                    score += 5
            except ValueError:
                pass

        notice_period = signals.get("notice_period_days", 90)
        if notice_period <= 30:
            score += 10
            reasons.append(f"Favorable notice footprint ({notice_period} days) for active founding-team onboarding.")
        elif notice_period > 60:
            score -= 10
            reasons.append(f"Extended notice timeline ({notice_period} days) flags deployment speed risks.")

        gh_score = signals.get("github_activity_score", -1)
        if gh_score > 60:
            score += 10
            reasons.append("Strong open-source or public code distribution presence.")

        final_score = max(0.0, min(100.0, score))
        reasoning_summary = " | ".join(reasons) if reasons else "Mainline profile compliance alignment."
        
        return final_score, reasoning_summary