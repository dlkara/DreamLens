import os
import openai
import json
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from .models import DreamDict


# ------------------------------
# 0. 공통 설정
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data" / "dream_clean.json"
openai.api_key = os.getenv("OPENAI_API_KEY")


# ------------------------------
# 1. 꿈 해몽
# ------------------------------

# TODO : 지우




# ------------------------------
# 2. 꿈 사전
# ------------------------------
def dream_dict_view(request):
    from django.conf import settings
    import os, json

    category = request.GET.get("category", "").replace('"', '')
    keyword_filter = request.GET.get("keyword", "").strip()

    with open(os.path.join(settings.BASE_DIR, 'data/dream_clean.json'), encoding='utf-8') as f:
        raw_data = json.load(f)

    sub_items = []
    keyword_list = []
    if category:
        items = raw_data.get(category, {})
        keyword_list = sorted(items.keys())  # ✅ 키워드 목록 추출
        seen_meanings = set()

        for keyword, entries in items.items():
            if keyword_filter and keyword != keyword_filter:
                continue
            for entry in entries:
                meaning = entry['해몽']
                if meaning not in seen_meanings:
                    sub_items.append({
                        "keyword": keyword,
                        "dream": entry["꿈"],
                        "interpret": meaning
                    })
                    seen_meanings.add(meaning)

    context = {
        "categories": list(raw_data.keys()),
        "selected_category": category,
        "selected_keyword": keyword_filter,
        "keywords": keyword_list,
        "sub_items": sub_items,
    }
    return render(request, "dict.html", context)


# ------------------------------
# 3. 꿈 조합기
# ------------------------------

def generate_interpretation(keywords):
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
    (2~3문장으로 요약)


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


def dream_combiner(request):
    context = {"loading": False}

    if request.method == "POST":
        kw1 = request.POST.get("kw1", "").strip()
        kw2 = request.POST.get("kw2", "").strip()
        kw3 = request.POST.get("kw3", "").strip()

        keywords = [k for k in [kw1, kw2, kw3] if k]

        context.update({"kw1": kw1, "kw2": kw2, "kw3": kw3})

        if 1 <= len(keywords) <= 3:
            context["loading"] = True

            result = generate_interpretation(keywords)
            try:
                _, interp = result.split("[해몽]", 1)
                interp, summary = interp.split("[요약]", 1)
            except:
                interp, summary = result, ""

            context.update({
                "interpretation": interp.strip(),
                "summary": summary.strip(),
                "loading": False,
            })

    return render(request, "combine.html", context)
