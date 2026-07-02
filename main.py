import os
from src.pipeline import DeepMatchPipeline

def main():
    data_file = os.path.join("data", "candidates.jsonl.gz")
    output_file = "team_submission.csv"
    if not os.path.exists(data_file):
        print("Required archive not detected inside data/ directory.")
        return
    pipeline = DeepMatchPipeline(data_file, output_file)
    pipeline.run()

if __name__ == "__main__":
    main()