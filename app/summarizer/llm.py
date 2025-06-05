from openai import OpenAI
from openai import OpenAIError
import time
import logging
from typing import Dict

from app.config.settings import OPENAI_API_KEY


logger = logging.getLogger('tech_trend_bot')

# Openai 클라이언트 초기화
def initialize_client():
    api_key = OPENAI_API_KEY
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 환경 변수에 없습니다")
    return OpenAI(api_key=api_key, timeout=60.0)

# 프롬프트 생성
def generate_prompt(content: str) -> Dict[str, str]:
    SYSTEM_PROMPT = """
[역할]
당신은 '테크 트렌드 커피챗' 내용을 요약하는 전문가야. 아래 요약 규칙을 따르며 정보를 구조화해서 정리해.

[요약 규칙]
1. 전체 내용을 5~6개의 명확한 카테고리로 분류해. 카테고리는 내용에 따라 자유롭게 새로 만들되, 비슷한 주제끼리 묶어야 해.
   - 예시 카테고리: AI & 빅테크 / Crypto & 금융 / 협업툴 & 개발툴 / 스타트업 & 비즈니스 / 산업 & 정책
   - 중복되거나 잘못된 분류는 피하고, 반드시 하나의 카테고리에만 배치해.
   - 각 카테고리는 고유한 이모지로 시작해 (🔵 🟣 🟡 🟢 🟠 🟤)

2. 주제가 누락되면 안돼. 반드시 본문에 있는 주제들의 80%는 다 요약에 들어가야 해.
   내용이 3줄 미만인 주제들은 짧게 (1-2줄만 써도 돼) 다 포함시켜줘:
   [주제 제목]
   <링크>  ← 링크가 있는 경우만 사용하고, 없으면 생략
   - 핵심 내용을 간결하고 명확하게 서술 (예: "기능이 출시됨", "지원 예정임", "발표함")
   - 중요 세부사항을 객관적으로 서술 (예: "성능이 2배 향상됨", "30% 증가함")

   내용이 3줄 이상으로 길거나 중요한 주제는 다음 형식으로 정리해:
   [주제 제목]
   <링크>  ← 링크가 있는 경우만 사용하고, 없으면 생략
   - 핵심 기능/변경사항 (예: "새로운 API가 출시됨")
   - 주요 특징/성능 (예: "처리 속도 50% 향상됨")
   - 구체적 수치/사례 (예: "현재 100개 기업이 도입 중임")
   - 시장 영향/전망 (예: "클라우드 시장 성장이 예상됨")

3. 문장 작성 규칙:
   - 모든 문장은 "~됨", "~함", "~임" 형식으로 끝나도록 작성
   - 구어체 표현 ("~야", "~네", "~어") 사용 금지
   - 간결하고 객관적인 서술식 사용
   - 불필요한 수식어 제거

4. 수치 및 사실 관계 처리:
   - 원문의 수치를 정확하게 인용하고, 절대 임의로 해석하거나 변경하지 않음
   - 비율(%)과 절대 수치를 명확히 구분하여 표현함
   - 인과 관계나 상관 관계를 명확하게 구분하여 서술함
   - 불확실한 정보는 "~로 예상됨", "~로 전망됨" 등으로 표현함

5. 전체 구조는 아래 예시처럼 구성해:

예시 출력 포맷:

☕️ 2025년 6월 4일 테크 트렌드 커피챗 요약

🔵 AI & 빅테크
[OpenAI: Codex 공개]
<https://openai.com/index/introducing-codex/>
- 클라우드 기반 코딩 에이전트 Codex가 출시됨
- 코드 작성 및 분석 자동화 기능이 포함됨
...
🟣 Crypto & 금융
...
""".strip()

    USER_PROMPT = f"""
다음은 커피챗 요약을 위한 원본 콘텐츠야. 위 가이드에 따라 구조화해서 요약해줘. 특히 수치와 사실 관계는 반드시 원문 그대로 유지하고, 잘못된 해석이나 과장된 표현을 사용하지 마:

{content}
    """.strip()

    return {
        "system": SYSTEM_PROMPT,
        "user": USER_PROMPT
    }

# GPT 호출 / 요약 생성
def get_summary(client, prompts: Dict[str, str]) -> str:
    retry_count = 0
    max_retries = 3
    base_delay = 1

    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompts["system"]},
                    {"role": "user", "content": prompts["user"]}
                ],
                temperature=0.3,
                max_tokens=8000,
                timeout=60
            )
            
            if not response.choices:
                raise ValueError("API 응답에 선택된 결과가 없습니다.")
            
            return response.choices[0].message.content

        except OpenAIError as e:
            wait_time = base_delay * (2 ** retry_count)
            if "rate_limit" in str(e).lower():
                logger.warning(f"Rate limit 도달. {wait_time}초 후 재시도... ({retry_count + 1}/{max_retries})")
            else:
                logger.warning(f"API 오류 발생. {wait_time}초 후 재시도... ({retry_count + 1}/{max_retries}): {str(e)}")
            
            time.sleep(wait_time)
            retry_count += 1
            
        except Exception as e:
            logger.error(f"예상치 못한 오류 발생: {str(e)}")
            raise
    
    raise Exception("최대 재시도 횟수를 초과했습니다.")
