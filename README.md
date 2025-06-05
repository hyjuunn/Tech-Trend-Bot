# Tech Trend Bot

A bot that automatically summarizes **Tech Trend Coffee Chat** content and shares the summary via **Slack**.

---

## Features

- Fetches content from **Notion**
- Summarizes it using **OpenAI GPT-4o model**
- Shares the summary in **Slack**
- Saves the summary to **MongoDB**

---

## Runtime Environment

- Python **3.11+**
- GitHub Actions (**scheduled job** support)

---

## Setup

### 1. Environment Variables

Set the following as **GitHub Actions secrets** or in a local `.env` file:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `NOTION_API_KEY` | Notion API key |
| `NOTION_DATABASE_ID` | Notion database ID |
| `SLACK_WEBHOOK_ALL_SHARE` | Slack webhook URL (public share) |
| `SLACK_WEBHOOK_JARVIS_TEST` | Slack webhook URL (test channel) |
| `MONGODB_CONNECTION_STRING` | MongoDB connection string |

### 2. GitHub Actions Secrets

Go to:  
**Repository → Settings → Secrets and variables → Actions**  
Add each variable listed above as a **secret**.

---

## Execution Schedule

- Runs **automatically** every **Wednesday at 1:00 PM KST**
- Can be **manually triggered** via GitHub Actions UI

---

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
