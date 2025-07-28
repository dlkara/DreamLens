import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_interpretation(user_dream, retrieved_items):
    """
    사용자 입력(user_dream)과 유사한 꿈(retrieved_items)을 기반으로 해몽을 생성합니다.
    """
    # retrieved_items 는 [{"꿈": ..., "해몽": ...}, ...] 형식이어야 함
    context = "\n".join([
        f"유사 꿈: {r.get('꿈', '(제목 없음)')}\n해몽: {r.get('해몽', '(해석 없음)')}"
        for r in retrieved_items
    ])

    prompt = f"""당신은 꿈 해몽 전문가입니다.
사용자가 꾼 꿈에 대해 아래 유사한 꿈과 해몽을 참고하여 간결하고 전문적인 해몽을 제공해주세요.

### 사용자 입력 꿈:
{user_dream}

### 유사 꿈 및 해몽:
{context}

### 해석:"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 꿈 해몽 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
