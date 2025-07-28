import os
import time
from dotenv import load_dotenv
import faiss
import json
import numpy as np
import openai

load_dotenv(r'../env/langchain_env.txt')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...') # OPENAI_API_KEY 필요!
#─────────────────────────────────────────────────────────────────────────────────────────
import streamlit as st

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.runnables.base import RunnableLambda
from langchain_core.runnables.passthrough import RunnablePassthrough
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain.storage.file_system import LocalFileStore
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.callbacks.base import BaseCallbackHandler

# 생성할 파일들의 경로를 미리 변수로 지정
# 폴더가 없을 경우를 대비해 생성해주는 로직 추가
# --- 1. 데이터 및 인덱스 로딩/생성 (기존 코드와 동일) ---

# --- 1. 데이터 및 인덱스 로딩/생성 (캐싱 적용) ---

# ⭐️ [수정] @st.cache_resource 데코레이터를 사용하여 이 함수 전체를 캐싱합니다.
# 이 함수는 앱 세션 동안 딱 한 번만 실행됩니다.
@st.cache_resource
def load_or_create_index_and_metadata():
    """
    Faiss 인덱스와 메타데이터를 로드하거나, 파일이 없으면 새로 생성합니다.
    이 함수의 결과는 캐시되어 반복 실행되지 않습니다.
    """
    os.makedirs("./embeddings", exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    index_path = r"./embeddings/dream.index"
    metadata_path = r"./data/meta_dream.json"
    original_data_path = r'./data/dream.json'

    if os.path.exists(index_path) and os.path.exists(metadata_path):
        print("✅ 기존 인덱스와 메타데이터를 캐시에서 불러옵니다.")
        faiss_index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        st.info("인덱스 파일을 찾을 수 없어 새로 생성합니다. 몇 분 정도 소요될 수 있습니다.")
        progress_bar = st.progress(0, text="데이터 준비 중...")

        try:
            with open(original_data_path, 'r', encoding='utf-8') as f:
                total_data = json.load(f)
        except FileNotFoundError:
            st.error(f"'{original_data_path}' 파일을 찾을 수 없습니다.")
            st.stop()

        documents, metadata = [], []
        for main_cat, sub_cats in total_data.items():
            for sub_cat, dreams in sub_cats.items():
                if isinstance(dreams, list):
                    for dream_item in dreams:
                        dream_text = dream_item.get('꿈', '').replace('"', '').strip()
                        interp_text = dream_item.get('해몽', '').strip()
                        main_cat_text = main_cat.replace('"', '').strip()
                        if dream_text and interp_text:
                            full_text = f"대분류: {main_cat_text}\n소분류: {sub_cat}\n꿈: {dream_text}\n해몽: {interp_text}"
                            documents.append(full_text)
                            metadata.append({"대분류": main_cat, "소분류": sub_cat, "꿈": dream_text, "해몽": interp_text})

        progress_bar.progress(20, text=f"총 {len(documents)}개의 문서를 임베딩합니다.")

        batch_size = 1000
        embedding_vectors = []
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            response = openai.embeddings.create(input=batch, model="text-embedding-3-small")
            embedding_vectors.extend([data.embedding for data in response.data])
            progress_percent = 20 + int(((i + len(batch)) / len(documents)) * 60)
            progress_bar.progress(progress_percent, text=f"{i + len(batch)}/{len(texts)} 문서 임베딩 완료...")
            time.sleep(1)

        embedding_vectors = np.array(embedding_vectors, dtype='float32')
        d = embedding_vectors.shape[1]
        progress_bar.progress(80, text="Faiss 인덱스를 구축합니다...")
        faiss_index = faiss.IndexFlatL2(d)
        faiss_index.add(embedding_vectors)
        faiss.write_index(faiss_index, index_path)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        progress_bar.progress(100, text="인덱스 생성 완료!")
        time.sleep(2)
        progress_bar.empty()
        st.success("✅ Faiss 인덱스와 메타데이터 생성이 완료되었습니다!")

    return faiss_index, metadata


# --- 2. Streamlit UI 구성 (LLM 연동 부분 수정) ---

# ⭐️ [수정] @st.cache_data 데코레이터를 사용하여 API 호출 함수를 캐싱합니다.
@st.cache_data
def get_embedding(text, model="text-embedding-3-small"):
    print(f"'{text[:20]}...'에 대한 임베딩을 생성합니다. (API 호출)")
    response = openai.embeddings.create(input=[text], model=model)
    return np.array([response.data[0].embedding], dtype='float32')


@st.cache_data
def generate_llm_response(user_dream, retrieved_data_json):
    """
    LLM 답변 생성 함수도 캐싱하여 동일한 요청에 대해 API 호출을 방지합니다.
    주의: retrieved_data는 리스트/딕셔너리라 직접 캐싱이 어려우므로 JSON 문자열로 변환하여 사용합니다.
    """
    print(f"'{user_dream[:20]}...'에 대한 LLM 답변을 생성합니다. (API 호출)")
    retrieved_data = json.loads(retrieved_data_json)
    reference_texts = []
    for i, item in enumerate(retrieved_data):
        clean_dream = item.get('꿈', '').strip()
        clean_interp = item.get('해몽', '').strip()
        reference_texts.append(f"{i + 1}. 꿈: {clean_dream}\n   해몽: {clean_interp}")

    reference_section = "\n\n".join(reference_texts)
    prompt = f"""
당신은 수십 년 경력의 매우 통찰력 있고 다정한 해몽 전문가, '꿈의 조각 연구소'의 연구원입니다.
당신의 임무는 사용자의 꿈 이야기를 듣고, 아래 제공된 [해몽 데이터베이스]에서 찾은 유사한 꿈의 상징과 의미를 바탕으로 사용자만을 위한 맞춤 해몽을 창조하는 것입니다.
---
[사용자 꿈 이야기]:
{user_dream}
---
[해몽 데이터베이스]:
{reference_section}
---
[작성 지침]:
- "사용자님의 꿈을 자세히 살펴보니..." 와 같이 친근하고 부드러운 말투로 시작해주세요.
- [해몽 데이터베이스]는 당신의 깊은 지식의 일부입니다. 사용자의 꿈과 데이터베이스의 내용이 완벽하게 일치하지 않더라도, 그 안의 상징과 의미를 창의적으로 연결하고 해석하여 자연스러운 하나의 이야기로 만들어주세요.
- **절대로 "참고 데이터에 따르면", "데이터베이스에 의하면" 또는 이와 유사한, 당신의 지식 출처를 직접적으로 언급하는 표현을 사용하지 마세요.** 모든 답변은 당신의 고유한 전문가적 분석인 것처럼 들려야 합니다.
- 사용자의 꿈 내용과 데이터베이스에서 찾은 상징들을 자연스럽게 엮어서 종합적인 해몽을 해주세요.
- 마지막으로, 종합적인 해몽을 바탕으로 사용자에게 도움이 될 만한 따뜻한 조언을 덧붙여주세요.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 매우 유능하고 다정한 해몽 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 답변 생성 중 오류가 발생했습니다: {e}"


# --- 앱 실행 ---
st.title("🔮 AI 꿈 해몽 연구소")
st.write("---")

# 캐시된 함수를 호출하여 데이터 로드
faiss_index, metadata = load_or_create_index_and_metadata()

user_dream = st.text_area("어떤 꿈을 꾸셨나요?", height=150, placeholder="돌아가신 할머니가 환하게 웃으며 돈을 주셨어요.")

if st.button("해몽 결과 보기"):
    if not user_dream:
        st.warning("꿈 내용을 입력해주세요.")
    else:
        with st.spinner("가장 비슷한 꿈을 찾고, AI가 최종 해몽을 생성하고 있습니다..."):
            # 캐시된 함수를 통해 사용자 꿈 임베딩 (동일한 꿈은 API 호출 안 함)
            query_vector = get_embedding(user_dream)

            k = 5
            distances, indices = faiss_index.search(query_vector, k)

            retrieved_results = [metadata[i] for i in indices[0]]
            # 캐싱을 위해 검색 결과를 JSON 문자열로 변환
            retrieved_results_json = json.dumps(retrieved_results)

            # 캐시된 함수를 통해 LLM 답변 생성 (동일한 꿈+검색결과는 API 호출 안 함)
            final_answer = generate_llm_response(user_dream, retrieved_results_json)

        st.subheader("🌙 AI가 들려주는 나의 꿈 이야기")
        st.markdown(final_answer)