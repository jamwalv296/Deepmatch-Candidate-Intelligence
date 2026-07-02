JD_TEXT = """
Senior AI Engineer Founding Team Redrob AI.
Own the intelligence layer ranking retrieval matching systems.
Production experience with embeddings based retrieval systems sentence-transformers OpenAI embeddings BGE E5 deployed to real users handled embedding drift index refresh retrieval quality regression in production.
Production experience with vector databases or hybrid search infrastructure Pinecone Weaviate Qdrant Milvus OpenSearch Elasticsearch FAISS operational experience.
Strong Python code quality.
Hands-on experience designing evaluation frameworks for ranking systems NDCG MRR MAP offline to online correlation A/B test interpretation.
LLM fine-tuning LoRA QLoRA PEFT learning to rank models XGBoost neural HR-tech recruiting tech marketplace products distributed systems large scale inference optimization open source contributions AI ML.
Ranking search recommendation systems shipped to real users at scale.
"""

MUST_HAVE_TERMS = [
    "embedding", "embeddings", "sentence-transformers", "sentence transformers",
    "bge", "e5", "openai embeddings", "vector database", "vector db",
    "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch",
    "faiss", "hybrid search", "hybrid retrieval", "retrieval", "ranking",
    "recommendation system", "search infrastructure", "python",
    "ndcg", "mrr", "map", "a/b test", "evaluation framework",
]

NICE_TO_HAVE_TERMS = [
    "lora", "qlora", "peft", "fine-tuning", "fine tuning", "learning to rank",
    "xgboost", "hr-tech", "hr tech", "recruiting tech", "marketplace",
    "distributed systems", "inference optimization", "open-source", "open source",
    "bm25", "tf-idf", "rag", "llm",
]

PROD_SHIP_TERMS = [
    "shipped", "deployed to real users", "production", "scale", "scaled",
    "real users", "recommendation system", "search system", "ranking system",
]

NON_TECH_TITLE_TERMS = ["marketing", "hr manager", "human resources", "sales",
                         "recruiter", "content writer", "operations manager", "finance"]
CORE_TECH_TITLE_TERMS = ["engineer", "scientist", "developer", "architect",
                          "researcher", "ml", "ai", "data"]

CV_SPEECH_ROBOTICS_TERMS = ["computer vision", "speech recognition", "robotics"]
NLP_IR_TERMS = ["nlp", "natural language", "retrieval", "search", "ranking",
                "information retrieval", "ir "]

RESEARCH_ONLY_TERMS = ["research scientist", "academic", "research lab",
                        "postdoc", "phd researcher"]
LANGCHAIN_ONLY_TERMS = ["langchain"]
PRE_LLM_TERMS = ["bm25", "elasticsearch", "faiss", "tf-idf", "recommendation system",
                  "search ranking", "learning to rank"]
TECH_LEAD_ARCHITECT_TERMS = ["tech lead", "architect", "engineering manager", "director"]

CONSULTING_FIRMS = ["tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini"]

PREFERRED_LOCATIONS = ["pune", "noida", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon", "gurugram"]

TITLE_CHASER_TITLES_ORDER = ["associate", "engineer", "senior", "staff", "principal", "lead"]
