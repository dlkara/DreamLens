import os
import json
import time
import numpy as np
import openai
import streamlit as st
from dotenv import load_dotenv

# --- 환경 변수 로드 ---
load_dotenv("../.env")
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- GPT 해몽 생성 ---
def generate_llm_from_keywords(keywords):
    keyword_text = ", ".join(keywords)

    prompt = f"""
당신은 한국의 전통 해몽 전문가이자 현대 심리학 상담가입니다.  
전통적 상징 해석과 함께, 사용자의 심리 상태와 현실적인 맥락도 고려해 해몽을 분석합니다.
당신의 임무는 사용자가 제시한 다음 [키워드 조합]이 꿈에서 함께 나타났을 때 가질 수 있는 상징적 의미를
한국 문화적 맥락에 맞춰 깊이 있게 분석하고 설명하는 것입니다.
또한 당신의 목표는 사용자가 제시한 키워드들이 조합된 꿈이  
심리적으로 어떤 의미를 가질 수 있는지 통합적으로 설명하는 것입니다.


[키워드 조합]:
{keyword_text}


[분석 지침]:
1. 각 키워드가 꿈에서 보편적으로 가지는 상징적 의미를 설명해주세요.
2. 특히 한국 문화권에서 해당 키워드들이 가지는 전통적인 해석(길몽/흉몽 등)을 우선적으로 고려해주세요.
   예: 돼지꿈 = 재물, 까마귀꿈 = 불길함, 용꿈 = 태몽/성공
3. 키워드 간의 조합이 가지는 복합적인 의미도 함께 분석해주세요.
4. 전통적인 상징으로 보기 어려운 키워드가 포함된 경우, 솔직하게 "최근의 관심사나 개인적인 경험이 반영된 것일 수 있다"고 안내해주세요.
5. 설명은 아래와 같이 구성해주세요:

[해몽]  
(해몽 내용)

[요약]  
(3줄 요약)


[예외 지침]:
- 키워드가 전통적 해몽에서 의미가 약한 경우, “이 키워드는 전통 해석보다는 사용자의 최근 관심사나 경험이 반영된 것일 수 있습니다.”라고 명확히 안내하세요.


[톤]:
- 따뜻하고 신뢰감 있는 말투
- 너무 단정적이기보다 조심스럽고 공감 가는 어조  
- 이모티콘/줄임말/구어체는 사용하지 마세요.
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
st.set_page_config("꿈 조합기", page_icon="🧩")
st.title("🧩 꿈 조합기")
st.markdown("키워드 1~3개를 입력하면, AI가 조합된 상징을 기반으로 새로운 해몽을 생성해요.")

col1, col2, col3 = st.columns(3)
with col1:
    kw1 = st.text_input("키워드 1", key="k1", placeholder="예: 불")
with col2:
    kw2 = st.text_input("키워드 2", key="k2", placeholder="예: 뱀")
with col3:
    kw3 = st.text_input("키워드 3", key="k3", placeholder="예: 어머니")

keywords = [kw.strip() for kw in [kw1, kw2, kw3] if kw.strip()]

if st.button("🔮 꿈 조합하기", disabled=not (1 <= len(keywords) <= 3)):
    with st.spinner("해몽 중입니다..."):
        llm_result = generate_llm_from_keywords(keywords)
        try:
            _, interp = llm_result.split("[해몽]", 1)
            interp, summary = interp.split("[요약]", 1)
        except:
            interp, summary = llm_result, ""

        st.subheader("🌙 해몽")
        st.markdown(interp.strip())

        st.subheader("🧾 요약")
        st.markdown(summary.strip())
