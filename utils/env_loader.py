import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    project_root = Path(__file__).resolve().parents[1]
    env_name = os.getenv("ENV", "dev").strip() or "dev"
    env_file = project_root / f".env.{env_name}"

    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=True)
    else:
        load_dotenv(dotenv_path=project_root / ".env", override=True)

    return project_root
