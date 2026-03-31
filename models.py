"""
Data models for the SQL Query Generation Environment.
"""
from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class SQLAction(Action):
    """Action for the SQL Query environment - a SQL query string."""
    sql_query: str = Field(..., description="The SQL query to answer the given question")


class SQLObservation(Observation):
    """Observation from the SQL Query environment."""
    question: str = Field(default="", description="Natural language question to answer with SQL")
    db_schema: str = Field(default="", description="Database schema available to query")
    task_id: str = Field(default="", description="Unique task identifier")
    difficulty: str = Field(default="easy", description="Task difficulty: easy, medium, or hard")
