import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# db connection
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

# webhook
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')
WEBHOOK_PATH = "/webhook"

# migrations
BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / 'db' / 'migrations'

