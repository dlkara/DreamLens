import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def embed_text(texts):
    """
    텍스트 리스트를 받아 OpenAI 임베딩을 수행한 후 벡터 리스트 반환
    """
    if not isinstance(texts, list):
        raise ValueError("입력은 리스트 형태여야 합니다.")

    # 텍스트 전처리
    cleaned = [text.strip().replace("\n", " ") for text in texts if isinstance(text, str) and text.strip()]

    if not cleaned:
        raise ValueError("임베딩할 텍스트가 없습니다.")

    print(f"🚀 임베딩 요청: {len(cleaned)}개")

    # 배치 처리 (OpenAI 제한 회피)
    vectors = []
    batch_size = 100  # 적당한 크기 (조정 가능)
    for i in range(0, len(cleaned), batch_size):
        batch = cleaned[i:i + batch_size]
        print(f"✅ Batch {i // batch_size + 1} completed. ({len(batch)} items)")

        response = openai.embeddings.create(
            input=batch,
            model="text-embedding-3-small"
        )
        vectors.extend([d.embedding for d in response.data])

    return vectors
