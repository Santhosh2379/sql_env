"""FastAPI application for the SQL Query Generation Environment."""
from openenv.core.env_server.http_server import create_app
from sql_env.models import SQLAction, SQLObservation
from sql_env.server.sql_env_environment import SQLEnvironment

app = create_app(
    SQLEnvironment,
    SQLAction,
    SQLObservation,
    env_name="sql_env",
    max_concurrent_envs=1,
)

def main(host: str = "0.0.0.0", port: int = 7860):
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == '__main__':
    main()
