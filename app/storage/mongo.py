from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config.settings import MONGODB_CONNECTION_STRING
from datetime import datetime
from typing import Dict, Any, Optional, Union
from datetime import date


# 요약본을 DB에 저장
def insert_summary_to_db(summary_data: Dict[str, Any]) -> bool:
    client: Optional[MongoClient] = None
    try:
        client = MongoClient(MONGODB_CONNECTION_STRING)
        
        # 연결 상태 확인
        client.admin.command('ping')
        
        db = client["Jarvis"]
        collection = db["tech_trend_coffee_chat_logs"]
        
        summary_date = datetime.strptime(summary_data["date"], "%Y-%m-%d")

        document = {
            "date": summary_date,
            "source": summary_data.get("source"),
            "sections": summary_data.get("sections", []),
            "createdAt": datetime.now(),
        }

        existing = collection.find_one({"date": summary_date})
        if existing:
            print(f"{summary_data['date']} 커피챗의 요약본이 이미 존재합니다.")
            return False
        
        collection.insert_one(document)
        print(f"{summary_data['date']} 커피챗의 요약본이 DB에 저장되었습니다.")
        return True

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise Exception(f"MongoDB 연결 실패: {str(e)}")
    
    except Exception as e:
        raise Exception(f"예상치 못한 오류 발생: {str(e)}")
    
    finally:
        if client:
            client.close()