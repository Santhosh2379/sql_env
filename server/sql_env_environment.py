"""
SQL Query Generation Environment Implementation.

A real-world environment where an AI agent must generate correct SQL queries
from natural language questions. Tasks range from simple SELECT statements
to complex multi-table JOINs and subqueries.
"""
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import SQLAction, SQLObservation
except ImportError:
    from models import SQLAction, SQLObservation


TASKS = [
    # EASY — simple SELECT queries
    {
        "task_id": "easy_1",
        "difficulty": "easy",
        "question": "Find the names and emails of all customers.",
        "db_schema": "customers(id, name, email, city)",
        "expected_keywords": ["select", "customers"],
        "required_columns": ["name", "email"],
    },
    {
        "task_id": "easy_2",
        "difficulty": "easy",
        "question": "Count the total number of employees in the company.",
        "db_schema": "employees(id, name, department, salary)",
        "expected_keywords": ["count", "employees"],
        "required_columns": ["count"],
    },
    {
        "task_id": "easy_3",
        "difficulty": "easy",
        "question": "List all products with a price greater than 100.",
        "db_schema": "products(id, name, price, category)",
        "expected_keywords": ["select", "products", "price"],
        "required_columns": ["name"],
    },
    # MEDIUM — JOINs and aggregations
    {
        "task_id": "medium_1",
        "difficulty": "medium",
        "question": "Find the total amount spent by each customer. Show customer name and total spending.",
        "db_schema": "customers(id, name, email), orders(id, customer_id, amount, date)",
        "expected_keywords": ["join", "sum", "group by"],
        "required_columns": ["name", "sum"],
    },
    {
        "task_id": "medium_2",
        "difficulty": "medium",
        "question": "Find employees whose salary is above the average salary in their department.",
        "db_schema": "employees(id, name, dept_id, salary), departments(id, dept_name)",
        "expected_keywords": ["avg", "salary", "employees"],
        "required_columns": ["name", "salary"],
    },
    {
        "task_id": "medium_3",
        "difficulty": "medium",
        "question": "List the top 5 products by total revenue.",
        "db_schema": "products(id, name, price), order_items(id, order_id, product_id, quantity)",
        "expected_keywords": ["join", "sum", "order by", "limit"],
        "required_columns": ["name"],
    },
    # HARD — subqueries, HAVING, complex conditions
    {
        "task_id": "hard_1",
        "difficulty": "hard",
        "question": "Find customers who placed more than 3 orders AND whose total spending exceeds $1000.",
        "db_schema": "customers(id, name, email), orders(id, customer_id, amount, date)",
        "expected_keywords": ["join", "sum", "having", "count", "group by"],
        "required_columns": ["name"],
    },
    {
        "task_id": "hard_2",
        "difficulty": "hard",
        "question": "For each department, find the employee with the highest salary. Show department name and employee name.",
        "db_schema": "employees(id, name, dept_id, salary), departments(id, dept_name)",
        "expected_keywords": ["join", "max", "group by"],
        "required_columns": ["dept_name", "name"],
    },
    {
        "task_id": "hard_3",
        "difficulty": "hard",
        "question": "Find products that have never been ordered. Show product name and price.",
        "db_schema": "products(id, name, price), order_items(id, order_id, product_id, quantity)",
        "expected_keywords": ["left join", "null"],
        "required_columns": ["name", "price"],
    },
]


def grade_sql(sql_query: str, task: dict) -> float:
    """
    Grade a SQL query against a task. Returns a score between 0.0 and 1.0.
    Provides partial credit for partial correctness.
    """
    sql_lower = sql_query.lower().strip()

    if not sql_lower or sql_lower in ("select 1", "select * from unknown_table"):
        return 0.0

    score = 0.0

    # 50% — keyword matching
    keyword_score = sum(1.0 for kw in task["expected_keywords"] if kw in sql_lower)
    keyword_score /= max(len(task["expected_keywords"]), 1)
    score += keyword_score * 0.5

    # 30% — required columns present
    column_score = sum(1.0 for col in task["required_columns"] if col in sql_lower)
    column_score /= max(len(task["required_columns"]), 1)
    score += column_score * 0.3

    # 10% — starts with SELECT (valid SQL)
    if sql_lower.startswith("select"):
        score += 0.1

    # 10% — references the correct table
    table_name = task["db_schema"].split("(")[0].strip().lower()
    if table_name in sql_lower:
        score += 0.1

    return round(min(score, 1.0), 3)


class SQLEnvironment(Environment):
    """
    SQL Query Generation Environment.

    The agent receives a natural language question and a database schema,
    and must generate the correct SQL query. Rewards are based on
    how closely the generated query matches the expected solution.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._task_index = 0
        self._current_task = None

    def reset(self) -> SQLObservation:
        """Reset the environment and return a new SQL task."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._current_task = TASKS[self._task_index % len(TASKS)]
        self._task_index += 1
        return SQLObservation(
            question=self._current_task["question"],
            db_schema=self._current_task["db_schema"],
            task_id=self._current_task["task_id"],
            difficulty=self._current_task["difficulty"],
            done=False,
            reward=0.0,
        )

    def step(self, action: SQLAction) -> SQLObservation:
        """Execute a step — grade the submitted SQL query."""
        self._state.step_count += 1
        reward = grade_sql(action.sql_query, self._current_task)
        done = self._state.step_count >= 3
        return SQLObservation(
            question=self._current_task["question"],
            db_schema=self._current_task["db_schema"],
            task_id=self._current_task["task_id"],
            difficulty=self._current_task["difficulty"],
            done=done,
            reward=reward,
        )

    @property
    def state(self) -> State:
        """Return current environment state."""
        return self._state
