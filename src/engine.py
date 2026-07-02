import json

class DeepMatchEngine:
    def __init__(self):
        self.ir_lexicon = ['bm25', 'tf-idf', 'tfidf', 'elasticsearch', 'opensearch', 'solr', 'faiss', 'milvus', 'qdrant', 'chroma', 'weaviate', 'pinecone', 'information retrieval', 'hybrid search', 'dense retrieval', 'sparse retrieval', 'inverted index', 'vector database', 'ranking systems']
        self.eval_lexicon = ['ndcg', 'mrr', 'map', 'recall@', 'precision@', 'discounted cumulative gain', 'mean reciprocal rank', 'mean average precision', 'ab testing', 'a/b testing', 'offline benchmark']
        self.product_lexicon = ['saas', 'product company', 'shipped to production', 'scale', 'latency', 'active users', 'deployment', 'deployed to real users', 'infrastructure', 'optimized inference', 'lora', 'qlora', 'fine-tuning', 'peft']
        self.consulting_lexicon = ['tcs', 'infosys', 'wipro', 'accenture', 'cognizant', 'capgemini', 'hcl', 'tech mahindra', 'pwc', 'ey', 'deloitte', 'kpmg', 'consulting', 'service-based']

    def extract_evidence(self, candidate):
        profile = candidate.get("profile", {}) or {}
        history = candidate.get("career_history", []) or []
        skills = [str(s.get("name", "")).lower() for s in candidate.get("skills", []) or []]
        signals = candidate.get("redrob_signals", {}) or {}
        
        current_title = str(profile.get("current_title", "")).lower()
        summary = str(profile.get("summary", "")).lower()
        all_text = f"{current_title} {summary} {' '.join(skills)} {' '.join([e.get('description', '') for e in history])}"

        evidence = {}
        
        tech_keywords = ['ai', 'ml', 'nlp', 'llm', 'transformer', 'engineer', 'developer']
        is_tech_profile = any(k in all_text for k in tech_keywords)
        is_non_tech_title = any(k in current_title for k in ['marketing', 'hr', 'sales', 'accountant'])
        coherence = 0.2 if (is_non_tech_title and is_tech_profile) else 1.0
        evidence['narrative'] = {'score': coherence, 'text': 'Consistent professional trajectory' if coherence > 0.5 else 'Narrative mismatch detected'}

        ir_hits = sum(1 for kw in self.ir_lexicon if kw in all_text)
        cap_score = min(1.0, ir_hits / 5)
        evidence['capability'] = {'score': cap_score, 'text': f'Found {ir_hits} IR/Search benchmarks' if ir_hits > 0 else 'Limited IR evidence'}

        product_hits = sum(1 for kw in self.product_lexicon if kw in all_text)
        car_score = min(1.0, product_hits / 4)
        evidence['career'] = {'score': car_score, 'text': 'Strong product development history' if car_score > 0.5 else 'Limited product shipping evidence'}

        resp = float(signals.get("recruiter_response_rate", 0.0) or 0.0)
        avail_score = 1.0 if resp > 0.7 else (0.5 if resp > 0.3 else 0.1)
        evidence['availability'] = {'score': avail_score, 'text': 'Highly responsive candidate' if avail_score > 0.5 else 'Low engagement signals'}

        return evidence

    def compute_final_score(self, evidence):
        if evidence['narrative']['score'] < 0.3:
            return 0.0, "Disqualified: Narrative Incoherence"
        
        score = (evidence['capability']['score'] * 0.4) + \
                (evidence['career']['score'] * 0.3) + \
                (evidence['availability']['score'] * 0.3)
        
        reasons = f"{evidence['capability']['text']}; {evidence['career']['text']}"
        return score, reasons