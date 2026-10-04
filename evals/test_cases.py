TEST_CASES = [
    {
        "id": "rag_001",
        "question": "What is the refund eligibility window?",
        "expected_route": "rag",
        "expected_source": "refund_policy.md",
        "expected_answer_contains": [
            "30 days"
        ],
    },
    {
        "id": "rag_002",
        "question": "How long are standard refund requests normally processed?",
        "expected_route": "rag",
        "expected_source": "refund_policy.md",
        "expected_answer_contains": [
            "5 business days"
        ],
    },
    {
        "id": "rag_003",
        "question": "What should happen when a customer has repeated payment failures?",
        "expected_route": "rag",
        "expected_source": "payment_policy.md",
        "expected_answer_contains": [
            "operational review"
        ],
    },
    {
        "id": "sql_001",
        "question": "How many transactions were refunded?",
        "expected_route": "sql",
        "expected_answer_contains": [
            "4"
        ],
    },
    {
        "id": "sql_002",
        "question": "How many customers are currently active?",
        "expected_route": "sql",
        "expected_answer_contains": [
            "9"
        ],
    },
    {
        "id": "sql_003",
        "question": "How many failed transactions are there?",
        "expected_route": "sql",
        "expected_answer_contains": [
            "3"
        ],
    },
    {
        "id": "sql_004",
        "question": "Which customers have failed payments and open support tickets?",
        "expected_route": "sql",
        "expected_answer_contains": ["David Wilson", "Frank Miller"],
    },
    {
        "id": "both_002",
        "question": "Which customers have refund-related support tickets and what does the refund policy say about processing time?",
        "expected_route": "both",
        "expected_answer_contains": ["5 business days"],
    },
]