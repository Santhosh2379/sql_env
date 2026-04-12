"""
Inference Script — SQL Query Generation Environment
===================================
MANDATORY variables:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
"""
import os
import json
import asyncio
from openai import OpenAI
from sql_env.client import SQLEnv
from sql_env.models import SQLAction

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")

MAX_STEPS = 3
TEMPERATURE = 0.2
MAX_TOKENS = 300

SYSTEM_PROMPT = """You are an expert SQL query writer.
Given a natural language question and a database schema, write a valid SQL query.
Reply with ONLY the SQL query — no explanations, no markdown, no code blocks.
Just the raw SQL query string."""


def build_user_prompt(observation) -> str:
    return f"""Database Schema:
{observation.db_schema}

Question: {observation.question}

Write the SQL query to answer this question."""


def parse_sql(response_text: str) -> str:
    if not response_text:
        return "SELECT 1"
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        text = "\n".join(lines).strip()
    return text


async def run_inference(base_url: str = "https://Santhosh1723-sql-env.hf.space", num_episodes: int = 3):
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    all_results = []
    total_reward = 0.0

    print("SQL Query Generation Environment — Inference")
    print("=" * 60)

    async with SQLEnv(base_url=base_url) as env:
        for episode in range(1, num_episodes + 1):
            print(f"\n📋 Episode {episode}/{num_episodes}")
            print("-" * 40)

            result = await env.reset()
            observation = result.observation

            print(f"  Task:     {observation.task_id} [{observation.difficulty.upper()}]")
            print(f"  Question: {observation.question}")

            episode_reward = 0.0

            for step in range(1, MAX_STEPS + 1):
                if result.done:
                    break

                user_prompt = build_user_prompt(observation)

                try:
                    completion = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                        stream=False,
                    )
                    response_text = completion.choices[0].message.content or ""
                except Exception as exc:
                    print(f"  ⚠ Model request failed: {exc}. Using fallback.")
                    response_text = "SELECT * FROM unknown_table"

                sql_query = parse_sql(response_text)
                print(f"  SQL: {sql_query[:100]}{'...' if len(sql_query) > 100 else ''}")

                result = await env.step(SQLAction(sql_query=sql_query))
                observation = result.observation
                episode_reward = result.reward or 0.0

                print(f"  Reward: {episode_reward:.3f} | Done: {result.done}")

                if result.done:
                    break

            total_reward += episode_reward
            all_results.append({
                "episode": episode,
                "task_id": observation.task_id,
                "difficulty": observation.difficulty,
                "reward": episode_reward,
            })

    avg_reward = total_reward / num_episodes
    print("\n" + "=" * 60)
    print(f"✅ Average Reward: {avg_reward:.3f}")
    print("=" * 60)

    output = {
        "average_reward": avg_reward,
        "num_episodes": num_episodes,
        "episodes": all_results,
    }
    with open("inference_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to inference_results.json")
    return output


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://Santhosh1723-sql-env.hf.space")
    parser.add_argument("--episodes", type=int, default=3)
    args = parser.parse_args()
    asyncio.run(run_inference(base_url=args.url, num_episodes=args.episodes))
