import os
import json
import time
import numpy as np
import openai
import streamlit as st
from dotenv import load_dotenv

# --- 환경 변수 로드 ---
load_dotenv(".env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- 데이터 로드 ---
@st.cache_resource
def load_data():
    with open("data/dream.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    all_dreams = []
    all_subcats = set()

    for main_cat, subcats in data.items():
        for subcat, entries in subcats.items():
            all_subcats.add(subcat)
            for entry in entries:
                dream_text = entry.get("꿈", "").strip()
                interp_text = entry.get("해몽", "").strip()
                if dream_text and interp_text:
                    all_dreams.append({
                        "대분류": main_cat,
                        "소분류": subcat,
                        "꿈": dream_text,
                        "해몽": interp_text
                    })
    return sorted(list(all_subcats)), all_dreams

# --- GPT 해몽 생성 ---
def generate_llm_from_subcats(subcats, examples):
    reference_texts = []
    for i, item in enumerate(examples[:5]):
        dream = item.get("꿈", "").strip()
        interp = item.get("해몽", "").strip()
        reference_texts.append(f"{i+1}. 꿈: {dream}\n   해몽: {interp}")

    context = "\n\n".join(reference_texts)
    keyword_text = ", ".join(subcats)

    prompt = f"""
    당신은 한국의 전통 해몽 지식과 현대 심리학을 아우르는, 매우 지혜로운 꿈 상징 분석 전문가입니다.
    당신의 임무는 사용자가 제시한 다음 [키워드 조합]이 꿈에서 함께 나타났을 때 가질 수 있는 상징적 의미를
    한국 문화적 맥락에 맞춰 깊이 있게 분석하고 설명하는 것입니다.

    [키워드 조합]:
    {keyword_text}

    [분석 지침]:
    1. 각 키워드가 꿈에서 보편적으로 가지는 상징적 의미를 설명해주세요.
    2. 특히 한국 문화권에서 해당 키워드들이 가지는 전통적인 해석(길몽/흉몽 등)을 우선적으로 고려해주세요.
       예: 돼지꿈 = 재물, 까마귀꿈 = 불길함, 용꿈 = 태몽/성공
    3. 키워드 간의 조합이 가지는 복합적인 의미도 함께 분석해주세요.
    4. 전통적인 상징으로 보기 어려운 키워드가 포함된 경우, 솔직하게 "최근의 관심사나 개인적인 경험이 반영된 것일 수 있다"고 안내해주세요.
    5. 설명은 아래와 같이 구성해주세요:

    [해몽시작]
    (해몽 내용: 각 키워드의 상징, 조합의 해석을 포함한 5~8줄 설명)

    [요약시작]
    (3줄 이내로 요약된 핵심 메시지)
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
st.set_page_config("🌙 소분류 조합 꿈 해몽기", page_icon="🧩")
st.title("🧩 소분류 조합 기반 꿈 해몽")
st.markdown("소분류 키워드를 1~3개 선택하면, 그 조합을 기반으로 AI가 새로운 꿈 해몽을 생성해요.")

subcats, dreams = load_data()

selected_subcats = st.multiselect("🗂️ 소분류 선택", subcats, max_selections=3)

if st.button("🔮 해몽 생성하기"):
    if not (1 <= len(selected_subcats) <= 3):
        st.warning("1~3개의 소분류를 선택해주세요.")
    else:
        # 선택된 소분류에 해당하는 해몽들 필터링
        matched = [d for d in dreams if d["소분류"] in selected_subcats]

        if not matched:
            st.warning("선택한 키워드에 해당하는 해몽 데이터를 찾을 수 없습니다.")
        else:
            with st.spinner("AI가 해몽을 생성 중입니다..."):
                llm_result = generate_llm_from_subcats(selected_subcats, matched)
                try:
                    _, interp = llm_result.split("[해몽시작]", 1)
                    interp, summary = interp.split("[요약시작]", 1)
                except:
                    interp, summary = llm_result, ""

                st.subheader("🌙 해몽")
                st.markdown(interp.strip())

                st.subheader("🧾 요약")
                st.markdown(summary.strip())
