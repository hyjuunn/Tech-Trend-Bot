from notion_client import Client
from app.config.settings import NOTION_API_KEY, NOTION_DATABASE_ID
from datetime import date, timedelta


# Notion Client 생성
notion = Client(auth = NOTION_API_KEY)

# Notion Database ID
DATABASE_ID = NOTION_DATABASE_ID

def get_database(database_id):
    return notion.databases.query(database_id=database_id)

def get_filtered_database(database_id, start_date=None, end_date=None):
    """지정된 날짜 범위의 데이터베이스 조회"""
    if not start_date:
        # 기본값: 이번주 월-금
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=4)
    
    # date 객체를 ISO 형식 문자열로 변환
    start_date_str = start_date.isoformat() if isinstance(start_date, date) else start_date
    end_date_str = end_date.isoformat() if isinstance(end_date, date) else end_date

    response = notion.databases.query(
        database_id=database_id,
        filter={
            "and": [
                {
                    "property": "회의일자",
                    "date": {
                        "on_or_after": start_date_str
                    }
                },
                {
                    "property": "회의일자",
                    "date": {
                        "on_or_before": end_date_str
                    }
                }
            ]
        }
    )
    return response

# Notion Page Block 조회
def get_page_blocks(page_id):
    blocks = []
    cursor = None

    while True:
        response = notion.blocks.children.list(
            block_id = page_id,
            start_cursor = cursor
        )
        blocks.extend(response.get("results", []))
        cursor = response.get("next_cursor")
        if cursor is None:
            break

    return blocks

def get_pages_blocks_by_date(database_id, start_date=None, end_date=None):
    """특정 날짜 범위의 페이지 블록 리스트 추출"""
    entry = get_filtered_database(database_id, start_date, end_date)
    result = []

    for page in entry.get("results", []):
        page_id = page.get("id")
        blocks = get_page_blocks(page_id)
        result.append({
            "page_id": page_id,
            "blocks": blocks
        })

    return result