import requests
from typing import Dict, List, Any
import json
import re
from app.config.settings import SLACK_WEBHOOK_JARVIS_TEST
from app.summarizer.formatter import format_summary_to_slack_message


def format_blocks_from_text(text: str) -> Dict[str, List[Dict[str, Any]]]:
    lines = text.strip().split("\n")
    blocks: List[Dict[str, Any]] = []

    if lines and lines[0]:
        # 앞에 디바이더 추가
        # blocks.append({"type": "divider"})
        header_text = lines[0]
        date_match = re.search(r"(\d{4})-(\d{2})-(\d{2})", header_text)
        if date_match:
            year, month, day = date_match.groups()
            formatted_date = f"{year}년 {int(month)}월 {int(day)}일"
            header_text = header_text.replace(f"{year}-{month}-{day}", formatted_date)
        
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*{header_text[:2900]}*"}
        })
        lines = lines[1:]

    current_section_text = ""

    block_count_limit = 48  # Slack 제한 - 제목(1), divider(1) 남겨두기

    def flush_section() -> None:
        nonlocal current_section_text
        if current_section_text.strip():
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": current_section_text.strip()[:2900]}
            })
        current_section_text = ""

    for line in lines:
        line = line.strip()
        # 빈 줄 처리 - 현재 섹션에 추가
        if not line:
            current_section_text += "\n"
            continue

        # 카테고리 시작:
        if re.match(r"^[🔵🟣🟡🟢🟠🟤]\s+\*", line):
            if len(blocks) >= block_count_limit:
                break
            flush_section()
            blocks.append({"type": "divider"})
            current_section_text += f"{line}\n\n"

        # 주제: • _제목_
        elif line.startswith("• _"):
            current_section_text += f"\n{line}\n"

        # 일반 내용
        else:
            current_section_text += f"{line}\n"

        # 블록 수 초과 방지
        if len(blocks) >= block_count_limit:
            break

    flush_section()

    # 제한 초과 시 마지막 안내 블록 추가
    if len(blocks) >= block_count_limit:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "_(이후 내용은 생략되었습니다: Slack 블록 수 제한 초과)_"}
        })

    return {"blocks": blocks}


def post_to_slack(webhook_url: str, message: Dict[str, Any]) -> bool:
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code != 200:
            raise Exception(f"Slack API 응답 오류: {response.text}")
        return True
    except Exception as e:
        raise Exception(f"Slack 전송 실패: {str(e)}")


def main() -> None:
    with open("formatted_summary.json", "r", encoding="utf-8") as f:
        summary_json = json.load(f)
        raw_text = format_summary_to_slack_message(summary_json)
    try:
        slack_message = format_blocks_from_text(raw_text)

        print("Slack에 메시지 전송 중...")
        success = post_to_slack(SLACK_WEBHOOK_JARVIS_TEST, slack_message)

        if success:
            print("메시지가 성공적으로 전송되었습니다!")
            print(f"채널 확인: {SLACK_WEBHOOK_JARVIS_TEST.split('/services/')[0]}")

    except Exception as e:
        print(f"오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
