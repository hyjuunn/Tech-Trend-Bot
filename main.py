import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import date, datetime, timedelta
from typing import Optional, Union

from app.notion.client import DATABASE_ID
from app.notion.parser import parse_notion_blocks_by_date, convert_all_parsed_pages_to_text
from app.summarizer.llm import initialize_client, generate_prompt, get_summary
from app.summarizer.formatter import format_summary_to_json, format_summary_to_slack_message
from app.storage.mongo import insert_summary_to_db
from app.slack.notifier import format_blocks_from_text, post_to_slack
from app.config.settings import SLACK_WEBHOOK_JARVIS_TEST


# 로그 디렉토리 생성
if not os.path.exists('logs'):
    os.makedirs('logs')

# 로거 설정 (INFO, WARNING, ERRoR)
logger = logging.getLogger('tech_trend_bot')
logger.setLevel(logging.INFO)

# 파일 핸들러 설정 (7일간 로그 보관, 최대 10MB)
file_handler = RotatingFileHandler(
    'logs/tech_trend_bot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=7
)
file_handler.setLevel(logging.INFO)

# 콘솔 핸들러 설정
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 로그 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 핸들러 로거 연결
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_this_week_dates() -> tuple[date, date]:
    """
    이번주 월요일과 금요일 날짜를 반환
    """
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday

def main(start_date: Optional[Union[str, date]] = None, end_date: Optional[Union[str, date]] = None) -> None:
    
    logger.info("테크 트렌드 커피챗 파이프라인 시작...")
    
    try:
        # 날짜 설정 (지정값 없으면 이번주 월 - 금 설정)
        if start_date is None or end_date is None:
            start_date, end_date = get_this_week_dates()
        else:
            # 문자열을 date 객체로 변환
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        logger.info(f"처리 기간: {start_date} ~ {end_date}")
        
        # 1. Notion에서 데이터 가져오기
        logger.info("1. Notion 데이터 파싱 중...")
        parsed_result = parse_notion_blocks_by_date(DATABASE_ID, start_date, end_date)
        if not parsed_result:
            logger.warning("해당 기간의 커피챗 데이터가 없습니다.")
            return
        
        # 2. 파싱된 데이터 텍스트로 변환
        parsed_texts = convert_all_parsed_pages_to_text(parsed_result)
        if not parsed_texts:
            logger.warning("파싱된 텍스트가 없습니다.")
            return
        
        # 3. GPT-4o로 요약 생성
        logger.info("2. GPT-4o로 요약 생성 중...")
        client = initialize_client()
        prompts = generate_prompt("".join(parsed_texts))
        summary = get_summary(client, prompts)
        if not summary:
            logger.warning("GPT-4o 요약 생성 실패")
            return
        
        # 4. 요약본 포맷팅
        logger.info("3. 요약본 포맷팅 중...")
        try:
            json_data = format_summary_to_json(summary)
        except ValueError as e:
            logger.error(f"JSON 변환 실패: {str(e)}")
            raise
        
        # 5. MongoDB에 저장
        logger.info("4. MongoDB에 저장 시도 중...")
        try:
            insert_summary_to_db(json_data)
        except Exception as e:
            logger.warning(f"MongoDB 저장 실패 (계속 진행): {str(e)}")
        
        # 6. Slack 메시지 전송
        logger.info("5. Slack 메시지 전송 중...")
        slack_text = format_summary_to_slack_message(json_data)
        slack_message = format_blocks_from_text(slack_text)
        post_to_slack(SLACK_WEBHOOK_JARVIS_TEST, slack_message)
        
        logger.info("모든 처리가 완료되었습니다!")
        
    except ValueError as e:
        logger.error(f"입력값 오류: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        # 기본: 이번주 데이터
        # 특정 날짜 설정시 main("YYYY-MM-DD", "YYYY-MM-DD")
        # main("2025-03-18", "2025-03-20")
        main()
        
    except Exception as e:
        logger.error("프로그램 종료 with 에러", exc_info=True)
        exit(1)
