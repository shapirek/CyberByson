from dotenv import load_dotenv
import os

load_dotenv()  # подгрузит .env в окружение

TOKEN = os.getenv("TOKEN")
TABULA = os.getenv("TABULA")
TABULA_kids = os.getenv("TABULA_KIDS")
SCHEDULE_SHEET_URL = os.getenv("SCHEDULE_SHEET_URL")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_LINK_PART = os.getenv("CHANNEL_LINK_PART")
GROUP_ID = os.getenv("GROUP_ID")
TIMEZONE = os.getenv("TIMEZONE")
