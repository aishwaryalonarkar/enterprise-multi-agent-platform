# Enterprise AI Analytics Platform

A production-oriented multi-agent analytics platform that combines structured enterprise data, unstructured documentation, and LLM-powered reasoning to answer business questions with grounded evidence.

The system uses **LangGraph** to orchestrate specialized agents for routing, SQL analytics, document retrieval, evidence validation, and final response generation.

## Architecture

```text
                         USER QUESTION
                              │
                              ▼
                     ┌─────────────────┐
                     │   SUPERVISOR    │
                     │      AGENT      │
                     └────────┬────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
               RAG                       SQL
                 │                         │
                 ▼                         ▼
          ┌─────────────┐          ┌─────────────┐
          │  RAG AGENT  │          │  SQL AGENT  │
          └──────┬──────┘          └──────┬──────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                     ┌─────────────────┐
                     │ VALIDATOR AGENT │
                     └────────┬────────┘
                              │
                              ▼
                       ANSWER AGENT
                              │
                              ▼
                        FINAL ANSWER
```

The supervisor determines whether a question requires:

* **RAG** — enterprise policies, procedures, and documentation
* **SQL** — structured enterprise records
* **Both** — questions requiring information from both sources

When both sources are required, the RAG and SQL agents execute as parallel branches before their evidence is passed to the validator.

## Key Features

### Multi-Agent Orchestration

Built with LangGraph using specialized agents:

* **Supervisor Agent** — determines the appropriate execution path
* **RAG Agent** — retrieves and summarizes relevant enterprise documentation
* **SQL Agent** — generates and executes read-only SQL queries against structured data
* **Validator Agent** — evaluates whether the combined evidence is sufficient
* **Answer Agent** — synthesizes the validated evidence into a concise response

### Enterprise RAG

The platform uses:

* OpenAI embeddings
* Chroma vector store
* Persistent document indexing
* Metadata-based source tracking
* Grounded response generation

Current knowledge base includes:

* Refund policy
* Payment policy
* Customer support policy

### Structured Data Analytics

The platform uses SQLite with enterprise-style datasets covering:

* Customers
* Transactions
* Support tickets

The SQL agent dynamically inspects the database schema and generates read-only `SELECT` queries.

Destructive SQL operations such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
CREATE
REPLACE
ATTACH
DETACH
```

are blocked by the current SQL execution layer.

### Evidence Validation

The validator evaluates evidence from both structured and unstructured sources.

It distinguishes between:

* complementary evidence
* missing evidence
* contradictory evidence
* unusable SQL results
* insufficient information

The final answer is generated only after successful validation.

### Observability

The workflow records trace information for each agent execution, including:

* Trace ID
* Agent/node name
* Execution duration
* Execution status
* Route selected by the supervisor
* RAG sources
* SQL query
* SQL row count
* Validation status
* Agent errors

Parallel RAG and SQL execution is supported through LangGraph state reducers, allowing trace events from concurrent branches to be merged safely.

## Evaluation

The project includes an evaluation suite covering:

* RAG routing
* SQL routing
* Multi-agent routing
* Retrieval/source correctness
* Expected answer content
* Validation success
* End-to-end workflow success
* Latency

Current evaluation:

| Metric             | Result |
| ------------------ | -----: |
| Test cases         |      8 |
| Passed             |      8 |
| Failed             |      0 |
| Routing accuracy   |   100% |
| Validation success |   100% |
| End-to-end success |   100% |
| Average latency    | 4.313s |

The evaluation suite currently covers questions such as:

* Refund eligibility
* Refund processing time
* Repeated payment failures
* Refunded transaction counts
* Active customer counts
* Failed transaction counts
* Customers with failed payments and open support tickets
* Questions requiring both database records and enterprise policy

## Project Structure

```text
enterprise-ai-analytics-platform/
│
├── app/
│   ├── agents/
│   │   ├── answer_agent.py
│   │   ├── rag_agent.py
│   │   ├── sql_agent.py
│   │   ├── supervisor.py
│   │   └── validator.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── observability/
│   │   └── tracer.py
│   │
│   ├── rag/
│   │
│   └── tools/
│       ├── rag_tools.py
│       └── sql_tools.py
│
├── data/
│   ├── documents/
│   │   ├── customer_support_policy.md
│   │   ├── payment_policy.md
│   │   └── refund_policy.md
│   │
│   ├── customers.csv
│   ├── transactions.csv
│   └── support_tickets.csv
│
├── evals/
│   ├── run_evaluation.py
│   └── test_cases.py
│
├── scripts/
│   ├── build_vector_store.py
│   └── setup_database.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Tech Stack

### AI & Agent Orchestration

* Python
* LangChain
* LangGraph
* OpenAI
* Pydantic

### Retrieval

* Chroma
* OpenAI Embeddings
* LangChain Chroma integration

### Data

* SQLite
* Pandas
* CSV
* Structured enterprise datasets

### Engineering

* Typed state management
* Read-only SQL execution
* Evaluation framework
* Workflow tracing
* Error instrumentation

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd enterprise-ai-analytics-platform
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env` to source control.

### 5. Create the SQLite database

```bash
python3 scripts/setup_database.py
```

### 6. Build the vector store

```bash
python3 scripts/build_vector_store.py
```

### 7. Run the application

```bash
python3 -m app.main
```

### 8. Run the evaluation suite

```bash
python3 -m evals.run_evaluation
```

## Example Questions

### Documentation / RAG

```text
What is the refund eligibility window?
```

```text
How long are standard refund requests normally processed?
```

### Structured SQL

```text
How many transactions were refunded?
```

```text
How many customers are currently active?
```

```text
Which customers have failed payments and open support tickets?
```

### Combined RAG + SQL

```text
Which customers have refund-related support tickets and what does the refund policy say about processing time?
```

This question requires both structured customer/support-ticket data and the refund policy.

## Design Goals

This project is designed around several engineering principles:

**Grounded answers**

Responses should be based on retrieved documentation and/or database evidence rather than unsupported model-generated information.

**Specialized agents**

Each agent has a narrow responsibility instead of relying on a single general-purpose LLM call.

**Controlled data access**

Database operations are restricted to read-only queries.

**Validation before response**

Evidence is evaluated before generating the final user-facing answer.

**Observable workflows**

Agent execution is instrumented so routing decisions, latency, errors, and intermediate results can be inspected.

**Evaluated behavior**

The system includes repeatable test cases instead of relying only on manual demonstrations.

## Current Status

Implemented:

* [x] Supervisor-based routing
* [x] RAG agent
* [x] SQL agent
* [x] Parallel RAG + SQL execution
* [x] Evidence validation
* [x] Answer synthesis
* [x] Persistent Chroma vector store
* [x] Read-only SQL execution
* [x] Workflow tracing
* [x] Agent-level latency tracking
* [x] Evaluation framework
* [x] Routing accuracy evaluation
* [x] End-to-end evaluation

Planned:

* [ ] Token usage and cost tracking
* [ ] Persistent trace storage
* [ ] Failure injection and recovery
* [ ] More robust SQL validation
* [ ] FastAPI service layer
* [ ] Dockerization
* [ ] CI/CD
* [ ] Cloud deployment
* [ ] Evaluation dashboard

## Why This Project?

Enterprise AI systems need more than an LLM prompt.

This project explores how to combine:

```text
LLMs
 +
Agent orchestration
 +
Structured data
 +
Enterprise documentation
 +
Validation
 +
Observability
 +
Evaluation
```

into a system that can be inspected, tested, and extended as an engineering application.
