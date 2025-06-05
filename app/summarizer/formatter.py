import re
from datetime import datetime
from typing import List, Dict
import json

# 커피챗 요약 텍스트를 JSON 형식으로 변환 (DB 저장용)
def format_summary_to_json(raw_text: str) -> Dict:
    date_match = re.search(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", raw_text)
    if not date_match:
        raise ValueError("날짜 형식이 없음.")
    year, month, day = map(int, date_match.groups())
    date_str = f"{year:04d}-{month:02d}-{day:02d}"

    sections_raw = re.split(r"\n([🔵🟣🟡🟢🟠🟤])\s*(.+?)\n", raw_text)
    # split 결과: [prefix, emoji, section_title, section_body, emoji, section_title, section_body, ...]

    #emoji 부분부터 section_body 부분까지 처리 반복
    sections: List[Dict] = []
    for i in range(1, len(sections_raw), 3):
        emoji = sections_raw[i].strip()
        category = sections_raw[i + 1].strip()
        section_body = sections_raw[i + 2].strip()

        #section_body 처리 -> 주제 기준으로 나누기
        item_blocks = re.split(r"\n(?=\[)", section_body)
        items = []
        for block in item_blocks:
            lines = block.strip().split("\n")
            if not lines:
                continue

            # 타이틀, 링크, 불릿 분리
            title_line = lines[0].strip()
            link_lines = [line for line in lines[1:] if line.startswith("<http") or line.startswith("http")]
            bullet_lines = [line.strip("- ").strip() for line in lines[1:] if not line.startswith("<http") and not line.startswith("http")]

            items.append({
                "title": title_line.strip("[]"),
                "link": link_lines[0] if link_lines else None,
                "bullets": bullet_lines
            })

        sections.append({
            "emoji": emoji,
            "category": category,
            "items": items
        })

    return {
        "date": date_str,
        "source": "테크 트렌드 커피챗",
        "sections": sections,
        "createdAt": datetime.now().isoformat()
    }

def save_json_to_file(json_data: dict, file_path = "formatted_summary.json"):
    try:
        with open(file_path, "w", encoding = "utf-8") as f:
            json.dump(json_data, f, ensure_ascii = False, indent = 2)
        print(f"JSON 파일이 {file_path}에 저장되었습니다")
    except Exception as e:
        print(f"저장 오류: {str(e)}")

# 커피챗 요약 텍스트를 슬랙 메시지 형식으로 변환
def format_summary_to_slack_message(summary_json: dict) -> str:
    lines = []

    date = summary_json.get("date", "")
    source = summary_json.get("source", "")
    header = f"☕️ {date} {source} 요약"
    lines.append(header)
    lines.append("")

    for section in summary_json.get("sections", []):
        emoji = section.get("emoji", "")
        category = section.get("category", "")
        lines.append(f"{emoji} *{category}*")
        lines.append("")
        for item in section.get("items", []):
            title = item.get("title", "").strip()
            link = item.get("link", [])
            bullets = item.get("bullets", [])

            if link:
                cleaned_link = re.sub(r"^<|>", "", link.strip())
                lines.append(f"• *_{title}_* | <{cleaned_link.strip()}|[링크]>")
            else:
                lines.append(f"• *_{title}_*")

            for bullet in bullets:
                if bullet.strip() and not bullet.strip().startswith("```"):
                    lines.append(f"> › {bullet.strip()}")
            lines.append("")
        lines.append("")
    return "\n".join(lines).strip()

def main():
    with open("coffee_chat_summary.txt", "r", encoding = "utf-8") as f:
        raw_text = f.read()
        json_data = format_summary_to_json(raw_text)
        save_json_to_file(json_data)
        slack_message = format_summary_to_slack_message(json_data)
        print(slack_message)

if __name__ == "__main__":
    main()
