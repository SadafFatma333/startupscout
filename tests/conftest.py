import os
from dotenv import load_dotenv

def pytest_configure():
    env_file = ".env.test" if os.path.exists(".env.test") else ".env.dev"
    load_dotenv(dotenv_path=env_file)
