
from ragas_evaluator import evaluate_response_quality

def main():
    
    scores = evaluate_response_quality(question="What happened during Apollo11?",answer="Apollo 11 landed on the moon in 1969.",contexts=["Apollo 11 was the first mission to land humans on the Moon...."])
    print(scores)

if __name__ == "__main__":
    main()