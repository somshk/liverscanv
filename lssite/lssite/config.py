import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

env_file = os.path.join(BASE_DIR, ".env")

if os.path.isfile(env_file):
    env.read_env(env_file)
