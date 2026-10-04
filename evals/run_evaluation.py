import time
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


from app.graph.workflow import run_workflow
from evals.test_cases import TEST_CASES

def check_contains(answer: str, expected_values: list[str]) -> bool:
    answer_lower = answer.lower()

    return all(
        value.lower() in answer_lower
        for value in expected_values
    )


def run_evaluation():

    results = []

    print("\n" + "=" * 70)
    print("ENTERPRISE MULTI-AGENT EVALUATION")
    print("=" * 70)

    for test_case in TEST_CASES:

        test_id = test_case["id"]
        question = test_case["question"]

        print(f"\nRunning: {test_id}")
        print(f"Question: {question}")

        start_time = time.perf_counter()

        try:
            result = run_workflow(question)

            latency = time.perf_counter() - start_time

            route = result.get("route")
            answer = result.get("final_answer", "")
            validation = result.get("validation_result", {})

            route_pass = (
                route == test_case["expected_route"]
            )

            answer_pass = check_contains(
                answer,
                test_case.get("expected_answer_contains", []),
            )

            validation_pass = (
                validation.get("status") == "valid"
            )

            source_pass = True

            expected_source = test_case.get("expected_source")

            if expected_source:
                rag_result = result.get("rag_result", {})
                sources = rag_result.get("sources", [])

                source_pass = expected_source in sources

            overall_pass = (
                route_pass
                and answer_pass
                and validation_pass
                and source_pass
            )

            test_result = {
                "id": test_id,
                "route_pass": route_pass,
                "answer_pass": answer_pass,
                "validation_pass": validation_pass,
                "source_pass": source_pass,
                "overall_pass": overall_pass,
                "latency_seconds": round(latency, 3),
            }

        except Exception as exc:

            latency = time.perf_counter() - start_time

            test_result = {
                "id": test_id,
                "route_pass": False,
                "answer_pass": False,
                "validation_pass": False,
                "source_pass": False,
                "overall_pass": False,
                "latency_seconds": round(latency, 3),
                "error": str(exc),
            }

        results.append(test_result)

        if not test_result["overall_pass"]:
            print("\n--- FAILURE DETAILS ---")
            print(f"Expected route: {test_case['expected_route']}")
            print(f"Actual route:   {route}")
            print(f"Answer:         {answer}")
            print(f"Validation:     {validation}")
            print(f"RAG result:     {result.get('rag_result')}")
            print(f"SQL result:     {result.get('sql_result')}")
            print(f"Trace:          {result.get('trace')}")
            print("-----------------------\n")
            
        print(
            f"Result: {'PASS' if test_result['overall_pass'] else 'FAIL'}"
        )

    return results


def print_summary(results):

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["overall_pass"]
    )

    route_passed = sum(
        1
        for result in results
        if result["route_pass"]
    )

    validation_passed = sum(
        1
        for result in results
        if result["validation_pass"]
    )

    latencies = [
        result["latency_seconds"]
        for result in results
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0
    )

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(f"Total test cases:     {total}")
    print(f"Passed:               {passed}")
    print(f"Failed:               {total - passed}")

    print(
        f"Routing accuracy:     "
        f"{route_passed / total * 100:.1f}%"
    )

    print(
        f"Validation success:   "
        f"{validation_passed / total * 100:.1f}%"
    )

    print(
        f"End-to-end success:   "
        f"{passed / total * 100:.1f}%"
    )

    print(
        f"Average latency:      "
        f"{average_latency:.3f}s"
    )

    print("=" * 70)


if __name__ == "__main__":

    results = run_evaluation()

    print_summary(results)