import os
import openai
import json
from pathlib import Path
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from .models import DreamDict
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import faiss
import numpy as np

from django.contrib.auth import get_user_model  # ✅ 현재 설정된 User 모델 반환

User = get_user_model()

# ------------------------------
# 0. 공통 설정
# ------------------------------
BASE_DIR = settings.BASE_DIR
JSON_PATH = BASE_DIR / "data" / "meta_dream.json"
openai.api_key = os.getenv("OPENAI_API_KEY")


def index(request):
    return render(request, "main.html")


# ------------------------------
# 1. 꿈 해몽
# ------------------------------
# 필요한 파일 경로들
INDEX_PATH = os.path.join(BASE_DIR, 'vectorDB', 'dream.index')
METADATA_PATH = os.path.join(BASE_DIR, 'data', 'meta_dream.json')
ORIGINAL_DATA_PATH = os.path.join(BASE_DIR, 'data', 'dream.json')

faiss_index = None
metadata = None
categories = {"대분류": [], "소분류": []}

try:
    # Faiss 인덱스와 메타데이터 로드
    print("✅ Django 서버 시작: 기존 인덱스와 메타데이터를 불러옵니다.")
    faiss_index = faiss.read_index(INDEX_PATH)
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # 분류 기준을 위한 카테고리 정보 로드
    with open(ORIGINAL_DATA_PATH, 'r', encoding='utf-8') as f:
        total_data = json.load(f)
    main_cats, sub_cats = set(), set()
    for main_cat, sub_cat_data in total_data.items():
        main_cats.add(main_cat.replace('"', ""))
        for sub_cat in sub_cat_data.keys():
            sub_cats.add(sub_cat)
    categories["대분류"] = sorted(list(main_cats))
    categories["소분류"] = sorted(list(sub_cats))

except Exception as e:
    print(f"⚠️ 경고: 데이터 로딩 중 오류 발생 ({e}). 해몽 기능이 정상 작동하지 않을 수 있습니다.")


# 꿈 해몽 LLM - AI 로직 함수
def get_embedding(text, model="text-embedding-3-small"):
    """사용자 텍스트를 OpenAI 임베딩으로 변환하는 함수"""
    response = openai.embeddings.create(input=[text], model=model)
    return np.array([response.data[0].embedding], dtype='float32')


def generate_llm_response(user_dream, retrieved_data, categories_data):
    """검색된 데이터와 분류 기준을 바탕으로 LLM에게 최종 답변을 요청하는 함수"""
    retrieved_data_json = json.dumps(retrieved_data, ensure_ascii=False)
    retrieved_items = json.loads(retrieved_data_json)
    reference_texts = []
    for i, item in enumerate(retrieved_items):
        clean_dream = item.get('꿈', '').strip()
        clean_interp = item.get('해몽', '').strip()
        reference_texts.append(f"{i + 1}. 꿈: {clean_dream}\n   해몽: {clean_interp}")

    reference_section = "\n\n".join(reference_texts)

    prompt = f"""
당신은 꿈 해몽과 분류에 매우 능숙한 AI 전문가입니다. 당신의 임무는 아래 정보를 바탕으로 사용자의 꿈을 분석하고, 네 부분으로 구성된 답변을 생성하는 것입니다.

---
[분류 기준 정보]
- 가능한 대분류: {categories_data['대분류']}
- 가능한 소분류: {categories_data['소분류']}

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

- **세 번째 부분**: `[키워드추출]`으로 시작합니다. 꿈의 의미를 압축하는 핵심 명사 키워드 3개를 쉼표(,)로 구분해서 나열하세요.

- **네 번째 부분**: `[요약시작]`으로 시작합니다. 상세 해몽의 내용을 세 개의 문장으로 요약합니다.
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


def dream_interpreter(request):
    context = {}
    # GET 요청
    if request.method == "GET":
        return render(request, 'interpret.html')

    # POST 요청 (해몽하기 버튼 눌렀을 시)
    elif request.method == "POST":
        dream = request.POST['input_text'].strip()

        context['dream'] = dream

        if dream and faiss_index is not None:
            # 1. 사용자 꿈 임베딩 및 Faiss 검색
            query_vector = get_embedding(dream)
            k = 5
            distances, indices = faiss_index.search(query_vector, k)
            retrieved_results = [metadata[i] for i in indices[0]]

            # 2. LLM 호출하여 원본 답변 생성
            raw_answer = generate_llm_response(dream, retrieved_results, categories)

            # 3. LLM 답변을 4개의 부분으로 파싱
            try:
                _, classification_part = raw_answer.split("[분류시작]", 1)
                classification_part, interpretation_part = classification_part.split("[해몽시작]", 1)
                interpretation_part, keywords_part = interpretation_part.split("[키워드추출]", 1)
                keywords_part, summary_part = keywords_part.split("[요약시작]", 1)

                context['classification_result'] = classification_part.strip()
                context['interpretation_result'] = interpretation_part.strip()
                context['keywords_result'] = keywords_part.strip()
                context['summary_result'] = summary_part.strip().replace('`', "")

                # print(classification_part.strip())
                # print(interpretation_part.strip())
                # print(keywords_part.strip())
                # print(summary_part.strip())

            except ValueError:
                # LLM이 형식에 맞지 않게 답변했을 경우를 대비한 예외 처리
                context['error'] = "AI가 답변을 생성하는 데 실패했습니다. 잠시 후 다시 시도해주세요."
                context['interpretation_result'] = raw_answer  # 원본 답변이라도 보여줌
        else:
            # 기타 오류 처리
            if not dream:
                context['error'] = "꿈 내용을 입력해주세요."
            else:
                context['error'] = "해몽 데이터베이스를 불러올 수 없습니다. 관리자에게 문의하세요."

        return render(request, 'interpret.html', context)

    # TODO: 로그인과 비로그인 따라 구분하기
    # 비로그인 사용자

    # 로그인 사용자


# ------------------------------
# 2. 꿈 사전
# ------------------------------
def dream_dict(request):
    # 1) 원본 JSON 로드
    json_fp = os.path.join(settings.BASE_DIR, 'data', 'meta_dream.json')
    with open(json_fp, encoding='utf-8') as f:
        raw = json.load(f)

    # 2) 클리닝 & 데이터 재구성
    data = []
    for item in raw:
        cat = item.get('대분류', '').strip().strip('"')
        sub = item.get('소분류', '').strip().strip('"')
        data.append({**item, '대분류': cat, '소분류': sub})

    # 3) 대분류 리스트
    categories = sorted({d['대분류'] for d in data})

    # 4) 소분류 flat 리스트 (cat-sub 쌍)
    sub_list = []
    seen = set()
    for d in data:
        pair = (d['대분류'], d['소분류'])
        if pair not in seen:
            seen.add(pair)
            sub_list.append({'cat': d['대분류'], 'sub': d['소분류']})

    # 5) GET 파라미터
    sel_cat = request.GET.get('category', '')
    sel_sub = request.GET.get('subcategory', '')

    # 6) 필터링된 결과
    filtered = []
    if sel_cat and sel_sub:
        filtered = [
            item for item in data
            if item['대분류'] == sel_cat and item['소분류'] == sel_sub
        ]

    return render(request, 'dict.html', {
        'categories': categories,
        'sub_list': sub_list,
        'filtered': filtered,
        'sel_cat': sel_cat,
        'sel_sub': sel_sub,
    })


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


# ------------------------------
# 4. 꿈 일기장  TODO : 현정
# ------------------------------

import calendar
from datetime import date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Diary

@login_required
def diary_list(request):
    today = date.today()
    year  = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # 이번 달 1일, 그리고 이전달/다음달 계산
    this_month_first = date(year, month, 1)
    prev_month_last  = this_month_first - timedelta(days=1)
    next_month_first = date(year, month, calendar.monthrange(year, month)[1]) + timedelta(days=1)

    prev_year, prev_month = prev_month_last.year, prev_month_last.month
    next_year, next_month = next_month_first.year, next_month_first.month

    # 달력 데이터
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    # 일기 데이터
    qs = Diary.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )
    # 분류별 날짜 집합 (예시)
    good_days   = {d.date.day for d in qs if getattr(d.dream_type, 'name','') == '길몽'}
    bad_days    = {d.date.day for d in qs if getattr(d.dream_type, 'name','') == '흉몽'}
    all_diary   = {d.date.day for d in qs}
    normal_days = all_diary - good_days - bad_days

    context = {
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'month_days': month_days,
        'today_day': (today.year == year and today.month == month) and today.day or 0,
        'good_days': good_days,
        'bad_days': bad_days,
        'normal_days': normal_days,
    }
    return render(request, 'diary-list.html', context)


def diary_detail(request):
    render(request, 'diary-detail.html')



# ------------------------------
# 5. 분석 리포트 TODO : 지우
# ------------------------------
def report(request):
    return render(request, "report.html")


# ------------------------------
# 6. 로그인/회원가입/마이페이지
# ------------------------------

# 로그인, 회원가입 - 안주경
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages

User = get_user_model()

from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse


def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        nickname = request.POST['nickname']
        birth = request.POST.get('birth', '')
        gender = request.POST.get('gender', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, "아이디 중복 확인을 해주세요")
            return redirect('register_user')

        if password != password2:
            messages.error(request, "비밀번호가 일치하지 않습니다")
            return redirect('register_user')

        # ✅ 닉네임을 별도로 저장
        user = User.objects.create_user(username=username, password=password)
        user.nickname = nickname  # ✅ 여기 중요!!
        if birth:
            try:
                user.birth = datetime.strptime(birth, "%Y%m%d").date()
            except ValueError:
                messages.error(request, "생년월일 형식이 올바르지 않습니다 (예: 20000101)")
                return redirect('register_user')
        if gender:
            user.gender = gender
        user.save()

        messages.success(request, "회원가입이 완료되었습니다. 로그인 후 이용해주세요.")
        return redirect('login')

    return render(request, 'register-user.html')


def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})





# 로그인
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # 메인 페이지로
        else:
            messages.error(request, '아이디 또는 비밀번호가 틀렸습니다.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')


# 마이페이지
from .forms import MyPageForm

# accounts/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from datetime import datetime

@login_required
def mypage(request):
    user = request.user

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        nickname = request.POST.get('nickname', '')
        birth_raw = request.POST.get('birth', '')  # 입력 이름 'birth'로 통일
        gender = request.POST.get('gender', '')

        # ✅ 닉네임 필수
        if not nickname:
            messages.error(request, "닉네임은 필수입니다.")
            return redirect('mypage')

        # ✅ 비밀번호 변경 시 입력값 확인
        if password or password2:
            if password != password2:
                messages.error(request, "비밀번호가 일치하지 않습니다.")
                return redirect('mypage')
            else:
                user.set_password(password)

        # ✅ 생년월일 선택 사항 처리
        if birth_raw:
            try:
                user.birth = datetime.strptime(birth_raw, "%Y%m%d").date()
            except ValueError:
                messages.error(request, "생년월일 형식이 올바르지 않습니다. (예: 19990101)")
                return redirect('mypage')
        else:
            user.birth = None  # 입력 안 했으면 비움

        # ✅ 나머지 필드 업데이트
        user.nickname = nickname
        user.gender = gender
        user.save()

        messages.success(request, "회원 정보가 수정되었습니다. 다시 로그인해주세요.")
        return redirect('login')  # 비밀번호 변경 가능성이 있으므로 로그인 페이지로 리다이렉트

    return render(request, 'mypage.html')

