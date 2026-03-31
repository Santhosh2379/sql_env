"""FastAPI application for the SQL Query Generation Environment."""
try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError("openenv is required. Install with 'uv sync'") from e

try:
    from models import SQLAction, SQLObservation
    from server.sql_env_environment import SQLEnvironment
except ModuleNotFoundError:
    from sql_env.models import SQLAction, SQLObservation
    from sql_env.server.sql_env_environment import SQLEnvironment

app = create_app(
    SQLEnvironment,
    SQLAction,
    SQLObservation,
    env_name="sql_env",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)
