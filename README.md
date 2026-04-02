---
title: Sql Env Environment Server
emoji: 🗄️
colorFrom: indigo
colorTo: purple
sdk: docker
pinned: false
app_port: 7860
tags:
  - openenv
  - sql
  - rl
---

# SQL Query Generation Environment

A real-world OpenEnv environment where an AI agent must generate correct SQL queries from natural language questions. Built for RL post-training of LLMs.

## What It Does

The agent receives:
- A **natural language question** (e.g. "Find all customers who spent more than $500")
- A **database schema** (e.g. `customers(id, name, email), orders(id, customer_id, amount)`)

And must generate the correct **SQL query** to answer the question.

## Quick Start

```python
from sql_env import SQLAction, SQLEnv

async with SQLEnv.from_env("Santhosh1723/sql-env") as env:
    result = await env.reset()
    print(f"Question: {result.observation.question}")
    print(f"Schema: {result.observation.db_schema}")

    result = await env.step(SQLAction(sql_query="SELECT name FROM customers"))
    print(f"Reward: {result.reward}")
```

## Tasks

| Difficulty | Example |
|------------|---------|
| 🟢 Easy | Simple SELECT with WHERE |
| 🟡 Medium | JOINs between 2 tables |
| 🔴 Hard | Subqueries + HAVING + aggregations |

9 tasks total — 3 easy, 3 medium, 3 hard.

## Reward Function

Scores SQL queries from **0.0 to 1.0** based on:
- Correct keywords (SELECT, JOIN, GROUP BY etc.) → 50%
- Required columns present → 30%
- Valid SQL structure → 10%
- Correct table referenced → 10%

## Action & Observation Spaces

**SQLAction**:
- `sql_query` (str) — The SQL query to submit

**SQLObservation**:
- `question` (str) — Natural language question
- `db_schema` (str) — Available database schema
- `task_id` (str) — Task identifier
- `difficulty` (str) — easy / medium / hard
- `reward` (float) — Score for submitted query
- `done` (bool) — Episode complete

## Running Locally

```bash
# Install dependencies
uv sync

# Start server
uv run server

# Run inference
python inference.py
```

## Baseline Score

Average reward: **0.900** across 3 episodes using `meta-llama/Llama-3.3-70B-Instruct`.

## Project Structure

```
sql_env/
├── __init__.py
├── client.py              # SQLEnv client
├── models.py              # SQLAction, SQLObservation
├── inference.py           # Baseline inference script
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Dependencies
└── server/
    ├── app.py             # FastAPI server
    ├── sql_env_environment.py  # Environment logic + grader
    └── Dockerfile         # Container definition
```
