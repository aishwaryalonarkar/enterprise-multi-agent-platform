from dotenv import load_dotenv
load_dotenv()

from app.graph.workflow import run_workflow




def main():

    questions = [
        "What is the refund eligibility window?",
        "How many transactions were refunded?",
        "Which customers have failed payments and open support tickets?",
    ]

    for question in questions:

        print("\n" + "=" * 70)
        print(f"QUESTION: {question}")
        print("=" * 70)

        result = run_workflow(question)

        print("\nROUTE:")
        print(result.get("route"))

        if result.get("rag_result"):
            print("\nRAG RESULT:")
            print(result["rag_result"])

        if result.get("sql_result"):
            print("\nSQL RESULT:")
            print(result["sql_result"])

        print("\nFINAL ANSWER:")
        print(result.get("final_answer"))

        print("\nVALIDATION:")
        print(result.get("validation_result"))
                


if __name__ == "__main__":
    main()