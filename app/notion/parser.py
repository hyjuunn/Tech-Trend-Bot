from app.notion.client import notion, get_pages_blocks_by_date
from typing import List, Dict, Any
import logging

logger = logging.getLogger('tech_trend_bot')

def parse_notion_blocks(blocks: List[Dict[str, Any]], indent_level: int = 0) -> List[str]:
    """
    노션 블록을 파싱하여 텍스트 형식으로 변환
    """
    parsed_blocks = []
    list_buffer = []
    list_type = None

    def flush_list():
        nonlocal list_buffer, list_type
        if not list_buffer:
            return

        if list_type == "bulleted_list_item":
            for item in list_buffer:
                marker = "->" * indent_level + "" if indent_level > 0 else "-"
                parsed_blocks.append(f"{marker} {item}")

        elif list_type == "numbered_list_item":
            for i, item in enumerate(list_buffer):
                if indent_level == 0:
                    parsed_blocks.append(f"{i + 1}. {item}")
                else:
                    marker = "->" * indent_level
                    parsed_blocks.append(f"{marker} {i + 1}. {item}")

        list_buffer = []
        list_type = None

    def extract_text(block: Dict[str, Any]) -> str:
        text_objects = block.get("rich_text", [])
        return " ".join(t.get("plain_text", "") for t in text_objects if isinstance(t, dict)).strip()

    for block in blocks:
        if not isinstance(block, dict):
            continue

        block_type = block.get("type")
        content = extract_text(block.get(block_type, {}))

        if not content:
            continue

        if block_type in ["paragraph", "quote"]:
            flush_list()
            if block_type == "quote":
                parsed_blocks.append(f"> {content}")
            else:
                parsed_blocks.append(content)

        elif block_type in ["bulleted_list_item", "numbered_list_item"]:
            if list_type is None:
                list_type = block_type
            elif list_type != block_type:
                flush_list()
                list_type = block_type
            list_buffer.append(content)

        elif block_type in ["heading_1", "heading_2", "heading_3"]:
            flush_list()
            heading_prefix = {
                "heading_1": "#",
                "heading_2": "##",
                "heading_3": "###"
            }.get(block_type, "##")
            parsed_blocks.append(f"{heading_prefix} {content}")

        if block.get("has_children"):
            try:
                child_blocks = notion.blocks.children.list(
                    block_id=block["id"],
                    page_size=100 
                ).get("results", [])
                
                child_parsed = parse_notion_blocks(child_blocks, indent_level + 1)
                flush_list()
                parsed_blocks.extend(child_parsed)
            except Exception as e:
                logger.error(f"하위 블록 가져오기 실패: {str(e)}")

    flush_list()
    return parsed_blocks

def parse_notion_blocks_by_date(database_id: str, start_date=None, end_date=None) -> List[Dict[str, Any]]:
    """특정 날짜 범위의 노션 블록 파싱"""
    pages = get_pages_blocks_by_date(database_id, start_date, end_date)
    parsed = []
    for page in pages:
        blocks = page.get("blocks", [])
        parsed_content = parse_notion_blocks(blocks)
        parsed.append({
            "page_id": page.get("page_id"),
            "parsed_content": parsed_content
        })
    return parsed

def convert_parsed_page_to_text(parsed_page: Dict[str, Any]) -> str:
    lines = parsed_page.get("parsed_content", [])
    result = []

    current_date = None
    current_author = None
    current_title = None
    current_links = []
    current_body = []

    def flush_article():
        nonlocal current_title, current_links, current_body
        if current_title or current_links or current_body:
            result.append(f"[제목] {current_title or '(제목 없음)'}")
            for link in current_links:
                result.append(f"[링크] {link}")
            if current_body:
                result.append("[내용]")
                result.extend(current_body)
            result.append("")
        current_title = None
        current_links = []
        current_body = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            flush_article()
            current_date = line[2:].strip()
            result.append(f"\n[날짜] {current_date}")
        elif line.startswith("@"):
            flush_article()
            current_author = line.strip()
            result.append(f"\n[작성자] {current_author}")
        elif line.startswith("##") or line.startswith("###"):
            flush_article()
            current_title = line.lstrip("#").strip()
        elif line.startswith("http"):
            current_links.append(line)
        else:
            current_body.append(line)

    flush_article()
    return "\n".join(result)

def convert_all_parsed_pages_to_text(parsed_pages: List[Dict[str, Any]]) -> List[str]:
    return [convert_parsed_page_to_text(page) for page in parsed_pages]