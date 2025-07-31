import os
import time
import json
import numpy as np
import openai
import streamlit as st
import faiss
from dotenv import load_dotenv

# --- 환경 변수 로드 ---
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- FAISS 인덱스와 메타데이터 로드 또는 생성 ---
@st.cache_resource
def load_data_and_build_index():
    os.makedirs("./embeddings", exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    index_path = "./embeddings/dream.index"
    metadata_path = "./data/meta_dream.json"
    original_data_path = "./data/dream.json"

    try:
        with open(original_data_path, 'r', encoding='utf-8') as f:
            total_data = json.load(f)
    except FileNotFoundError:
        st.error(f"'{original_data_path}' 파일이 필요합니다.")
        st.stop()

    if os.path.exists(index_path) and os.path.exists(metadata_path):
        faiss_index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        st.info("인덱스를 새로 생성합니다.")
        documents, metadata = [], []
        for main_cat, sub_cats in total_data.items():
            for sub_cat, dreams in sub_cats.items():
                for dream_item in dreams:
                    dream_text = dream_item.get('꿈', '').strip()
                    interp_text = dream_item.get('해몽', '').strip()
                    if dream_text and interp_text:
                        full_text = f"꿈: {dream_text}\n해몽: {interp_text}"
                        documents.append(full_text)
                        metadata.append({"대분류": main_cat, "소분류": sub_cat, "꿈": dream_text, "해몽": interp_text})

        vectors = []
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i+batch_size]
            response = openai.embeddings.create(input=batch, model="text-embedding-3-small")
            vectors.extend([r.embedding for r in response.data])
            time.sleep(1)

        vector_array = np.array(vectors).astype("float32")
        faiss_index = faiss.IndexFlatL2(vector_array.shape[1])
        faiss_index.add(vector_array)
        faiss.write_index(faiss_index, index_path)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    return faiss_index, metadata

# --- 임베딩 생성 ---
@st.cache_data(show_spinner=False)
def get_embedding(text, model="text-embedding-3-small"):
    response = openai.embeddings.create(input=[text], model=model)
    return np.array([response.data[0].embedding], dtype='float32')

# --- 키워드 조합 검색 ---
@st.cache_data(show_spinner=False)
def search_by_keywords(keywords, _faiss_index, metadata, top_k=5):
    query_text = " ".join(keywords)
    query_vector = get_embedding(query_text)
    distances, indices = _faiss_index.search(query_vector, top_k)
    return [metadata[i] for i in indices[0]]

# --- GPT 해몽 생성 ---
@st.cache_data(show_spinner=False)
def generate_llm_from_keywords(keywords, reference_data):
    reference_texts = []
    for i, item in enumerate(reference_data):
        dream = item.get("꿈", "").strip()
        interp = item.get("해몽", "").strip()
        reference_texts.append(f"{i+1}. 꿈: {dream}\n   해몽: {interp}")

    context = "\n\n".join(reference_texts)
    keyword_text = ", ".join(keywords)

    prompt = f"""
당신은 꿈 해몽 전문가입니다.

아래는 유사한 꿈 사례들입니다:

{context}

이 데이터를 참고해서, '{keyword_text}'라는 키워드를 조합한 꿈에 대해 해몽을 작성해주세요.
다음 네 가지 구성으로 답해주세요. 각 항목은 반드시 다음 구분자로 시작하세요.

[해몽시작] ...  
[요약시작] ...  

해몽은 부드럽고 친절한 말투로 작성해주세요.
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 숙련된 꿈 해몽가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

# --- Streamlit UI ---
st.set_page_config("꿈 조합기", page_icon="💡")
st.title("💡 꿈 조합기")
st.markdown("키워드 1~3개를 입력하면 AI가 꿈의 해몽을 지어줘요.")

faiss_index, metadata = load_data_and_build_index()

user_keywords = st.text_input("키워드 입력 (쉼표로 구분)", placeholder="예: 불, 뱀, 어머니")
if st.button("🔮 해몽 생성"):
    keywords = [kw.strip() for kw in user_keywords.split(",") if kw.strip()]
    if not (1 <= len(keywords) <= 3):
        st.warning("1~3개의 키워드를 입력해주세요.")
    else:
        with st.spinner("GPT가 해몽을 생성 중입니다..."):
            retrieved = search_by_keywords(keywords, faiss_index, metadata)
            gpt_result = generate_llm_from_keywords(keywords, retrieved)

            try:
                _, interp = gpt_result.split("[해몽시작]", 1)
                interp, summary = interp.split("[요약시작]", 1)
            except Exception:
                interp, summary = gpt_result, ""

            st.subheader("🌙 해몽")
            st.markdown(interp.strip())

            st.subheader("🧾 요약")
            st.markdown(summary.strip())
