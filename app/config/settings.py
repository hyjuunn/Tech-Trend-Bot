from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Notion
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Slack
SLACK_WEBHOOK_ALL_SHARE = os.getenv("SLACK_WEBHOOK_ALL_SHARE")
SLACK_WEBHOOK_JARVIS_TEST = os.getenv("SLACK_WEBHOOK_JARVIS_TEST")

#Mongodb
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
