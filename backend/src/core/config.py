import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging
import json

load_dotenv(override=True)

DB_APP_USER=os.environ.get("DB_APP_USER")
DB_APP_PASSWORD=os.environ.get("DB_APP_PASSWORD")
DB_APP_PORT=os.environ.get("DB_APP_PORT")
DB_APP_HOST=os.environ.get("DB_APP_HOST")
DB_APP_NAME=os.environ.get("DB_APP_NAME")
