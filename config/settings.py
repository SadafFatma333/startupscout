import os
from dotenv import load_dotenv

# Explicitly load .env.dev if exists
if os.path.exists(".env.dev"):
    load_dotenv(".env.dev")
else:
    load_dotenv()

print("Loading .env from:", os.getcwd())
load_dotenv()
print("Reddit vars:", os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_USER_AGENT"))

# -----------------------
# Environment selection
# -----------------------

# default to 'dev' if ENV not set
ENV = os.getenv("ENV", "dev")

# load the corresponding .env file (e.g., .env.dev or .env.prod)
env_file = f".env.{ENV}"
if os.path.exists(env_file):
    load_dotenv(dotenv_path=env_file)
else:
    # in cloud prod, env vars often come directly from platform
    load_dotenv()

# -----------------------
# Path configuration
# -----------------------

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
STARTUP_DATA_FILE = os.path.join(DATA_DIR, "startup_data.json")

# -----------------------
# Helper for required vars
# -----------------------

def require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    return value

# -----------------------
# Database configuration
# -----------------------

if ENV == "prod":
    # Railway PostgreSQL provides these standard variables
    DB_CONFIG = {
        "dbname": os.getenv("PGDATABASE") or require_env("DB_NAME"),
        "user": os.getenv("PGUSER") or require_env("DB_USER"),
        "password": os.getenv("PGPASSWORD") or require_env("DB_PASSWORD"),
        "host": os.getenv("PGHOST") or require_env("DB_HOST"),
        "port": int(os.getenv("PGPORT") or os.getenv("DB_PORT", 5432)),
    }
else:  # dev / test
    DB_CONFIG = {
        "dbname": os.getenv("DB_NAME", "startupscout"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", 5432)),
    }

# -----------------------
# Embedding configuration
# -----------------------

EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "minilm")

if EMBEDDING_BACKEND == "openai":
    OPENAI_API_KEY = require_env("OPENAI_API_KEY")
else:
    OPENAI_API_KEY = None

# -----------------------
# Admin and cache configuration
# -----------------------
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "changeme")
REDIS_URL = os.getenv("REDIS_URL")

# LangFuse configuration
LANGFUSE_ENABLED = os.getenv("LANGFUSE_ENABLED", "false").lower() in ("1", "true", "yes")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "").strip()
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip()
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "").strip()
LANGFUSE_SAMPLING_RATE = float(os.getenv("LANGFUSE_SAMPLING_RATE", "0.25"))  # 25% default
