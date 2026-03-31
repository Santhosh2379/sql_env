"""SQL Query Generation Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import SQLAction, SQLObservation


class SQLEnv(EnvClient[SQLAction, SQLObservation, State]):
    """
    Client for the SQL Query Generation Environment.

    Example:
        >>> async with SQLEnv(base_url="http://localhost:8000") as client:
        ...     result = await client.reset()
        ...     print(result.observation.question)
        ...     result = await client.step(SQLAction(sql_query="SELECT * FROM customers"))
        ...     print(result.reward)
    """

    def _step_payload(self, action: SQLAction) -> Dict:
        return {"sql_query": action.sql_query}

    def _parse_result(self, payload: Dict) -> StepResult[SQLObservation]:
        obs_data = payload.get("observation", {})
        observation = SQLObservation(
            question=obs_data.get("question", ""),
            db_schema=obs_data.get("db_schema", ""),
            task_id=obs_data.get("task_id", ""),
            difficulty=obs_data.get("difficulty", "easy"),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
        )
        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
