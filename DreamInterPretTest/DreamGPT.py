import os
import time
from dotenv import load_dotenv
import faiss
import json
import numpy as np
import openai
import streamlit as st


# --- 환경 변수 로드 ---
load_dotenv(r'../env.txt')
print(f'\tOPENAI_API_KEY={os.getenv("OPENAI_API_KEY")[:20]}...')


@st.cache_resource
def load_data_and_build_index():
    """
    Faiss 인덱스, 메타데이터, 그리고 분류를 위한 카테고리 목록을 로드하거나 생성합니다.
    이 함수의 결과는 캐시되어 반복 실행되지 않습니다.
    """
    os.makedirs("./embeddings", exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    index_path = r"./embeddings/dream.index"
    metadata_path = r"./data/meta_dream.json"
    original_data_path = r'./data/dream.json'

    categories = {"대분류": set(), "소분류": set()}

    try:
        with open(original_data_path, 'r', encoding='utf-8') as f:
            total_data = json.load(f)
        for main_cat, sub_cats in total_data.items():
            categories["대분류"].add(main_cat.replace('"', ""))
            for sub_cat in sub_cats.keys():
                categories["소분류"].add(sub_cat)
        categories["대분류"] = sorted(list(categories["대분류"]))
        categories["소분류"] = sorted(list(categories["소분류"]))

    except FileNotFoundError:
        st.error(f"분류를 위해 원본 데이터 파일인 '{original_data_path}' 파일이 반드시 필요합니다.")
        st.stop()

    if os.path.exists(index_path) and os.path.exists(metadata_path):
        print("✅ 기존 인덱스와 메타데이터를 캐시에서 불러옵니다.")
        faiss_index = faiss.read_index(index_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        st.info("인덱스 파일을 찾을 수 없어 새로 생성합니다. 몇 분 정도 소요될 수 있습니다.")
        progress_bar = st.progress(0, text="데이터 준비 중...")

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
            progress_bar.progress(progress_percent, text=f"{i + len(batch)}/{len(documents)} 문서 임베딩 완료...")
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

    return faiss_index, metadata, categories


@st.cache_data(show_spinner=False)
def get_embedding(text, model="text-embedding-3-small"):
    print(f"'{text[:20]}...'에 대한 임베딩을 생성합니다. (API 호출)")
    response = openai.embeddings.create(input=[text], model=model)
    return np.array([response.data[0].embedding], dtype='float32')


@st.cache_data(show_spinner=False)
def generate_llm_response(user_dream, retrieved_data_json, categories):
    print(f"'{user_dream[:20]}...'에 대한 분류, 답변, 요약을 생성합니다. (API 호출)")
    retrieved_data = json.loads(retrieved_data_json)
    reference_texts = []
    for i, item in enumerate(retrieved_data):
        clean_dream = item.get('꿈', '').strip()
        clean_interp = item.get('해몽', '').strip()
        reference_texts.append(f"{i + 1}. 꿈: {clean_dream}\n   해몽: {clean_interp}")

    reference_section = "\n\n".join(reference_texts)

    # ✨ [수정] AI가 제목이나 번호를 붙이지 않고 내용만 출력하도록 프롬프트 지침을 수정
    prompt = f"""
당신은 꿈 해몽과 분류에 매우 능숙한 AI 전문가입니다. 당신의 임무는 아래 정보를 바탕으로 사용자의 꿈을 분석하고, 네 부분으로 구성된 답변을 생성하는 것입니다.

---
[분류 기준 정보]
- 가능한 대분류: {categories['대분류']}
- 가능한 소분류: {categories['소분류']}

[해몽 참고 정보]
- 유사한 꿈 데이터베이스:
{reference_section}
---
[사용자 꿈 이야기]:
{user_dream}
---
[작업 지침 및 출력 형식]:
당신은 반드시 아래 4개의 부분으로 구성된 답변을 생성해야 합니다.
각 부분은 지정된 구분자로 시작해야 합니다.
**절대로, 절대로 각 부분에 제목이나 번호(예: "2. 상세 해몽:")를 붙이지 마세요. 오직 내용만 작성해야 합니다.**

- **첫 번째 부분**: `[분류시작]`으로 시작합니다. [분류 기준 정보]를 참고하여 "대분류: [선택]\n소분류: [선택]" 형식으로 꿈을 분류하세요. 일치하는 것이 없으면 "대분류: 해당 없음\n소분류: 해당 없음" 이라고 적으세요.

- **두 번째 부분**: `[해몽시작]`으로 시작합니다. "사용자님의 꿈을 자세히 살펴보니..." 와 같이 친근한 말투로 시작하여 상세한 해몽과 따뜻한 조언을 작성하세요.

- **세 번째 부분**: `[키워드추출]`으로 시작합니다. 꿈의 의미를 압축하는 핵심 명사 키워드 3~4개를 쉼표(,)로 구분해서 나열하세요.

- **네 번째 부분**: `[요약시작]`으로 시작합니다. 상세 해몽의 내용을 세 개의 문장으로 요약합니다. 각 문장은 글머리 기호(-)로 시작해도 좋습니다.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 꿈을 분석하고, 분류하고, 해몽하고, 요약하는 다재다능한 AI 전문가입니다."},
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

faiss_index, metadata, categories = load_data_and_build_index()

user_dream = st.text_area("어떤 꿈을 꾸셨나요?", height=150, placeholder="돌아가신 할머니가 환하게 웃으며 돈을 주셨어요.")

if st.button("해몽 결과 보기"):
    if not user_dream:
        st.warning("꿈 내용을 입력해주세요.")
    else:
        with st.spinner("AI가 꿈을 분석하고 해몽을 작성하고 있습니다..."):
            query_vector = get_embedding(user_dream)
            k = 5
            distances, indices = faiss_index.search(query_vector, k)
            retrieved_results = [metadata[i] for i in indices[0]]
            retrieved_results_json = json.dumps(retrieved_results, ensure_ascii=False)

            raw_answer = generate_llm_response(user_dream, retrieved_results_json, categories)

            try:
                # 더 안정적인 파싱을 위해 순서대로 분리
                _, classification_part = raw_answer.split("[분류시작]", 1)
                classification_part, interpretation_part = classification_part.split("[해몽시작]", 1)
                interpretation_part, keywords_part = interpretation_part.split("[키워드추출]", 1)
                keywords_part, summary_part = keywords_part.split("[요약시작]", 1)

            except ValueError:
                # LLM이 형식에 맞지 않게 답변했을 경우를 대비한 예외 처리
                classification_part = "분류 정보를 가져오는데 실패했습니다."
                interpretation_part = raw_answer
                keywords_part = "키워드를 추출하는데 실패했습니다."
                summary_part = "요약 정보를 가져오는데 실패했습니다."

        # 분리된 각 부분을 화면에 표시
        st.subheader("📊 AI가 분석한 나의 꿈 종류")
        st.success(classification_part.strip())

        st.subheader("🌙 AI가 들려주는 나의 꿈 이야기")
        st.markdown(interpretation_part.strip())

        st.subheader("🔑 꿈의 핵심 키워드")
        st.info(keywords_part.strip())

        st.write("---")
        st.subheader("✨ 세 줄 요약")

        summary_part_cleaned = summary_part.strip().replace("undefined", "").strip()
        st.info(summary_part_cleaned)