import os
import openai
import json
import faiss
import numpy as np
from pathlib import Path
import pytz
from collections import defaultdict, Counter

import calendar
from datetime import date
from datetime import datetime
from datetime import timezone as py_timezone  # 표준 UTC용
from django.utils import timezone  # Django 시간대 처리용
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model  # 현재 설정된 User 모델 반환
User = get_user_model()

from django.db.models import Count

from .models import Interpretation
from .models import DreamDict
from .models import Diary
from .forms import DiaryForm
from .forms import MyPageForm

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

                # 로그인한 사용자일 시, 해몽로그를 DB 에 저장하고 해당 로그의 pk를 session 에 저장
                # 세션에 저장된 pk로 찾아서 일기장 작성에 뿌려준다.
                if request.user.is_authenticated:
                    interpretation = Interpretation(
                        user=request.user,
                        input_text=dream,
                        result=context['interpretation_result'],
                        keywords=context['keywords_result'],
                        summary=context['summary_result'],
                    )

                    interpretation.save()
                    context['interpret_pk'] = interpretation.pk

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
# 4. 꿈 일기장
# ------------------------------
@login_required
def diary_list(request, yyyymm=None):
    # 1) 파라미터 없으면 오늘 기준으로 리다이렉트
    if yyyymm is None:
        today = timezone.localdate()
        return redirect('diary_list', yyyymm=today.year * 100 + today.month)

    # 2) 연·월 분해
    year = yyyymm // 100
    month = yyyymm % 100

    # 3) 오늘 하이라이트용
    today = timezone.localdate()
    today_day = today.day if (today.year == year and today.month == month) else None

    # 4) 이전/다음 달 계산
    first_of_month = date(year, month, 1)
    prev_dt = first_of_month - relativedelta(months=1)
    next_dt = first_of_month + relativedelta(months=1)
    prev_yyyymm = prev_dt.year * 100 + prev_dt.month
    next_yyyymm = next_dt.year * 100 + next_dt.month

    # 5) KST 기준 월초/다음월초를 UTC-aware로 계산
    tz = timezone.get_current_timezone()
    start_local = timezone.make_aware(datetime(year, month, 1, 0, 0), tz)
    if month == 12:
        ny, nm = year + 1, 1
    else:
        ny, nm = year, month + 1
    end_local = timezone.make_aware(datetime(ny, nm, 1, 0, 0), tz)
    start_utc = start_local.astimezone(pytz.UTC)
    end_utc = end_local.astimezone(pytz.UTC)

    # 6) 해당 기간의 일기 조회 (pk 오름차순)
    qs = Diary.objects.filter(
        user=request.user,
        date__gte=start_utc,
        date__lt=end_utc,
    ).order_by('pk')

    # 7) 날짜별 색상용 정보(day_info)와 모달용 엔트리(entries_by_day) 수집
    day_info = {}
    entries_by_day = defaultdict(list)
    for entry in qs:
        d = timezone.localtime(entry.date).day

        # 첫 번째(=가장 작은 pk) 일기로만 색상 정보 등록
        if d not in day_info:
            day_info[d] = {
                'pk': entry.pk,
                'dream_type': entry.dream_type_id,
            }

        # 모달용: interpretation.input_text 앞 20자 잘라서 title로 사용
        interp = getattr(entry, 'interpretation', None)
        raw = interp.input_text if interp else ''
        snippet = raw[:20] + '…' if len(raw) > 20 else raw

        entries_by_day[d].append({
            'pk': entry.pk,
            'title': snippet,
        })

    # 8) 달력용 2D 배열 생성 (일요일 시작)
    cal = calendar.Calendar(firstweekday=6)
    raw_weeks = cal.monthdayscalendar(year, month)

    month_days = []
    for week in raw_weeks:
        row = []
        for day in week:
            if day == 0:
                # 빈 칸
                row.append({
                    'day': None,
                    'pk': None,
                    'is_good': False,
                    'is_bad': False,
                    'is_normal': False,
                })
            else:
                info = day_info.get(day)
                if info:
                    pk = info['pk']
                    t = info['dream_type']
                    is_good = (t == 1)
                    is_bad = (t == 2)
                    is_normal = not (is_good or is_bad)
                else:
                    pk = None
                    is_good = False
                    is_bad = False
                    is_normal = False

                row.append({
                    'day': day,
                    'pk': pk,
                    'is_good': is_good,
                    'is_bad': is_bad,
                    'is_normal': is_normal,
                })
        month_days.append(row)

    # 9) 컨텍스트에 JSON 직렬화된 entries_by_day 포함
    context = {
        'year': year,
        'month': month,
        'today_day': today_day,
        'month_days': month_days,
        'prev_yyyymm': prev_yyyymm,
        'next_yyyymm': next_yyyymm,
        'entries_by_day_json': json.dumps(entries_by_day),
    }

    return render(request, 'diary-list.html', context)


@login_required
def diary_detail(request, pk):
    try:
        # 먼저 pk로 일기가 존재하는지 check
        diary = Diary.objects.get(pk=pk)

        # 일기가 존재한다면, 현재 로그인한 사용자의 것인지 확인
        if diary.user == request.user:
            # 본인의 일기가 맞으면, 정상적으로 상세 페이지를 보여줍니다.
            return render(request, 'diary-detail.html', {'diary': diary})
        else:
            # 일기는 존재하지만, 다른 사람의 것일 경우
            access_limit_message = "다른 사람의 일기는 열람할 수 없습니다."
            return render(request, 'diary-access-limit.html', {
                'access_limit_message': access_limit_message,
            })

    except Diary.DoesNotExist:
        # DB에 해당 pk의 일기가 아예 존재하지 않을 경우
        error_message = "존재하지 않는 일기입니다."
        return render(request, 'diary-access-limit.html', {
            'error_message': error_message,
        })


@login_required
def diary_write(request):
    if request.method == "GET":
        return render(request, "inaccessible.html")
        # form = DiaryForm()
        # return render(request, 'diary-write.html', {
        #     'form': form,
        # })

    elif request.method == "POST":
        context = {}
        context['interpretation'] = Interpretation.objects.get(pk=request.POST['interpret_pk'])
        context['form'] = DiaryForm()

        return render(request, "diary-write.html", context)


def diary_writeOk(request):
    if request.method == 'POST':
        context = {}
        form = DiaryForm(request.POST)
        if form.is_valid():
            diary = form.save(commit=False)
            diary.user = request.user
            diary.interpretation = Interpretation.objects.get(pk=request.POST['interpret_pk'])
            diary.save()

            context['pk'] = diary.pk
            # print(context, diary.pk)
            return render(request, 'diary-writeOk.html', context)


def diary_update(request, pk):
    """
    pk에 해당하는 꿈 일기를 수정하는 뷰
    """
    try:
        # 먼저 pk로 일기가 존재하는지 check
        diary = Diary.objects.get(pk=pk)

        # 일기가 존재한다면, 현재 로그인한 사용자의 것인지 확인
        if diary.user == request.user:
            if request.method == "GET":
                form = DiaryForm(instance=diary)
                # 본인의 일기가 맞으면, 정상적으로 상세 페이지로 ㄱㄱ
                return render(request, 'diary-update.html', {'form': form, 'diary': diary})

            elif request.method == "POST":
                form = DiaryForm(request.POST, instance=diary)
                if form.is_valid():
                    form.save()  # 유효성 검사를 통과하면 DB에 변경사항을 저장합니다.
                    return render(request, 'diary-updateOk.html', {'pk': diary.pk})  # 수정 후 상세 페이지로 이동합니다.

        else:
            # 일기는 존재하지만, 다른 사람의 것일 경우
            access_limit_message = "다른 사람의 일기는 수정할 수 없습니다."
            return render(request, 'diary-access-limit.html', {
                'access_limit_message': access_limit_message,
            })

    except Diary.DoesNotExist:
        # DB에 해당 pk의 일기가 아예 존재하지 않을 경우
        error_message = "존재하지 않는 일기입니다."
        return render(request, 'diary-access-limit.html', {
            'error_message': error_message,
        })


def diary_updateOk(request, pk):
    return render(request, 'diary-updateOk.html', {'pk': pk})


def diary_delete(request):
    if request.method == "POST":
        try:
            pk = request.POST['pk']
            diary = Diary.objects.get(pk=pk)
            deleted_count, _ = diary.delete() # DELETE => Tuple[int, dict[str, int]]
                          # (deleted_count, deleted_dict)
                          # (삭제된 개체수, 모델별 삭제수)
        except Diary.DoesNotExist:
            deleted_count = 0
    return render(request, 'diary-delete.html', {'result': deleted_count})


# ------------------------------
# 5. 분석 리포트 -> TODO : 현정, 지우
# ------------------------------
@login_required()
def report_base(request):
    # 현재 날짜 기준으로 리다이렉트
    today = timezone.localdate()
    yyyymm = today.year * 100 + today.month
    return redirect('report', yyyymm=yyyymm)


@login_required
def report(request, yyyymm):
    year = yyyymm // 100
    month = yyyymm % 100

    # 현재 연/월 기준 날짜
    today = date.today()
    first_of_month = date(year, month, 1)

    # 이전/다음 월 계산
    prev_dt = first_of_month - relativedelta(months=1)
    next_dt = first_of_month + relativedelta(months=1)
    prev_yyyymm = prev_dt.year * 100 + prev_dt.month
    next_yyyymm = next_dt.year * 100 + next_dt.month

    # 시작/끝 UTC
    tz = timezone.get_current_timezone()
    start_local = timezone.make_aware(datetime(year, month, 1), tz)
    end_local = timezone.make_aware(datetime(next_dt.year, next_dt.month, 1), tz)
    start_utc = start_local.astimezone(py_timezone.utc)
    end_utc = end_local.astimezone(py_timezone.utc)

    diaries = Diary.objects.filter(
        user=request.user,
        date__gte=start_utc,
        date__lt=end_utc
    ).select_related('emotion', 'dream_type', 'interpretation')

    # 차트용 데이터 처리
    dream_counts = (
        diaries.values('dream_type__type')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    dream_labels = [item['dream_type__type'] for item in dream_counts]
    dream_data = [item['count'] for item in dream_counts]

    emotion_counts = (
        diaries.values('emotion__name', 'emotion__icon')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    emotion_labels = [item['emotion__name'] for item in emotion_counts]
    emotion_icons = [item['emotion__icon'] for item in emotion_counts]
    emotion_data = [item['count'] for item in emotion_counts]

    # 키워드 수집
    keywords_counter = Counter()
    for diary in diaries:
        interp = diary.interpretation
        if interp and interp.keywords:
            keywords = [k.strip() for k in interp.keywords.split(',') if k.strip()]
            keywords_counter.update(keywords)
    keyword_items = list(keywords_counter.items())  # ex. [('돈', 3), ('연애', 2)]

    context = {
        'year': year,
        'month': month,
        'prev_yyyymm': prev_yyyymm,
        'next_yyyymm': next_yyyymm,

        # 현재 날짜 기준 미래인 경우, 다음 달 링크 비활성화
        'today_yyyymm': today.year * 100 + today.month,
        'year_list': list(range(2023, today.year + 1)),
        'month_list': list(range(1, 13)),

        # 해당 연/월에 diary 데이터 존재 여부
        'has_data': diaries.exists(),

        # 차트 정보
        'dream_labels': json.dumps(dream_labels, ensure_ascii=False),
        'dream_data': json.dumps(dream_data),
        'emotion_labels': json.dumps(emotion_labels, ensure_ascii=False),
        'emotion_icons': json.dumps(emotion_icons, ensure_ascii=False),
        'emotion_data': json.dumps(emotion_data),

        # 워드 클라우드 정보
        'keywords': json.dumps(keyword_items, ensure_ascii=False),
    }
    return render(request, 'report.html', context)


# ------------------------------
# 6. 로그인/회원가입/마이페이지
# ------------------------------

# 로그인, 회원가입
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

        # 닉네임을 별도로 저장
        user = User.objects.create_user(username=username, password=password)
        user.nickname = nickname
        if birth:
            try:
                user.birth = datetime.strptime(birth, "%Y-%m-%d").date()  # 수정됨!
            except ValueError:
                messages.error(request, "생년월일 형식이 올바르지 않습니다 (예: 2000-01-01)")
                return redirect('register_user')

        if gender:
            user.gender = gender
        user.save()

        messages.success(request, "회원가입이 완료되었습니다. 로그인 후 이용해주세요.", extra_tags='signup')
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
@login_required
def mypage(request):
    user = request.user

    if request.method == 'POST':
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        nickname = request.POST.get('nickname', '')
        birth_raw = request.POST.get('birth', '')  # 입력 이름 'birth'로 통일
        gender = request.POST.get('gender', '')

        # 닉네임 필수
        if not nickname:
            messages.error(request, "닉네임은 필수입니다.")
            return redirect('mypage')

        # 비밀번호 변경 시 입력값 확인
        if password or password2:
            if password != password2:
                messages.error(request, "비밀번호가 일치하지 않습니다.")
                return redirect('mypage')
            else:
                user.set_password(password)

        # 생년월일 선택 사항 처리
        if birth_raw:
            try:
                user.birth = datetime.strptime(birth_raw, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "생년월일 형식이 올바르지 않습니다. (예: 1999-01-01)")
                return redirect('mypage')

        else:
            user.birth = None  # 입력 안 했으면 비움

        # 나머지 필드 업데이트
        user.nickname = nickname
        user.gender = gender
        user.save()

        messages.success(request, "회원 정보가 수정되었습니다. 다시 로그인해주세요.")
        return redirect('login')  # 비밀번호 변경 가능성이 있으므로 로그인 페이지로 리다이렉트

    return render(request, 'mypage.html')
