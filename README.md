# Tech Trend Bot

테크 트렌드 커피챗 내용을 자동으로 요약하고 공유하는 봇입니다.

## 기능

- Notion에서 커피챗 내용을 가져옴
- OpenAI GPT를 사용하여 내용을 요약
- 요약된 내용을 Slack으로 공유
- MongoDB에 요약 내용 저장

## 실행 환경

- Python 3.11+
- GitHub Actions (크론 작업)

## 설정 방법

1. 환경 변수 설정
   - `OPENAI_API_KEY`: OpenAI API 키
   - `NOTION_API_KEY`: Notion API 키
   - `NOTION_DATABASE_ID`: Notion 데이터베이스 ID
   - `SLACK_WEBHOOK_ALL_SHARE`: Slack 웹훅 URL (전체 공유용)
   - `SLACK_WEBHOOK_JARVIS_TEST`: Slack 웹훅 URL (테스트용)
   - `MONGODB_CONNECTION_STRING`: MongoDB 연결 문자열

2. GitHub Actions 설정
   - 저장소의 Settings > Secrets and variables > Actions에서 위의 환경 변수들을 시크릿으로 추가

## 실행 스케줄

- 매주 수요일 오후 2시 (KST)에 자동 실행
- GitHub Actions 페이지에서 수동 실행도 가능

## 로컬 실행 방법

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

2. .env 파일 생성 및 환경 변수 설정
   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 필요한 값들을 설정
   ```

3. 실행
   ```bash
   python main.py
   ```
