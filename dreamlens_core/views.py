# DREAMLens Django views.py with FAISS index error handling
import json
import os
import numpy as np
import faiss
from django.shortcuts import render
from django.conf import settings
from openai import OpenAI

# OpenAI client 초기화
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# FAISS 인덱스 및 메타데이터 경로
INDEX_PATH = os.path.join(settings.BASE_DIR, 'vectorDB', 'dream.index')
META_PATH = os.path.join(settings.BASE_DIR, 'vectorDB', 'dream_meta.json')

# 인덱스와 메타데이터 로드 시도
faiss_index = None
DREAM_META = None
META_IS_DICT = False
META_KEYS = []

try:
    faiss_index = faiss.read_index(INDEX_PATH)
except Exception as e:
    # 인덱스 파일 누락 또는 로드 오류
    print(f"[ERROR] FAISS index load failed: {e}")

try:
    with open(META_PATH, 'r', encoding='utf-8') as f:
        DREAM_META = json.load(f)
    if isinstance(DREAM_META, dict):
        META_IS_DICT = True
        META_KEYS = list(DREAM_META.keys())
    else:
        META_IS_DICT = False
except Exception as e:
    print(f"[ERROR] Meta JSON load failed: {e}")


def interpret_dream(request):
    interpretation = None
    error = None

    # 인덱스나 메타 없으면 사용자에 안내
    if faiss_index is None or DREAM_META is None:
        error = (
            "검색용 FAISS 인덱스 또는 메타데이터 파일을 찾을 수 없습니다. "
            "프로젝트 루트에서 build_index.py 스크립트를 실행하여 'dream.index'와 'dream_meta.json'을 생성해주세요."
        )
        return render(request, 'dreams/interpret.html', {'interpretation': None, 'error': error})

    if request.method == 'POST':
        dream_input = request.POST.get('dream_input', '').strip()
        if not dream_input:
            error = '꿈 내용을 입력해주세요.'
        else:
            # 1) 입력 텍스트 임베딩
            embed_resp = client.embeddings.create(
                model='text-embedding-ada-002',
                input=[dream_input]
            )
            embedding = np.array(embed_resp.data[0].embedding, dtype='float32').reshape(1, -1)

            # 2) FAISS 인덱스 검색 (상위 5개)
            distances, indices = faiss_index.search(embedding, 5)
            top_idxs = indices[0]

            # 3) 검색 결과로부터 심볼·설명 추출
            retrieved = []
            for idx in top_idxs:
                try:
                    if META_IS_DICT and idx < len(META_KEYS):
                        sym = META_KEYS[idx]
                        desc = DREAM_META[sym]
                    elif not META_IS_DICT and idx < len(DREAM_META):
                        item = DREAM_META[idx]
                        sym = item.get('symbol') or item.get('key') or str(idx)
                        desc = item.get('description') or item.get('desc') or item.get('meaning') or ''
                    else:
                        continue
                    retrieved.append({'symbol': sym, 'description': desc})
                except Exception:
                    continue

            # 4) 컨텍스트 생성
            if not retrieved:
                error = '관련 꿈 상징을 찾을 수 없습니다.'
            else:
                context = '관련 꿈 상징:\n'
                for item in retrieved:
                    context += f"- {item['symbol']}: {item['description']}\n"

                # 5) LLM 프롬프트 메시지
                messages = [
                    {
                        'role': 'system',
                        'content': (
                            '당신은 수십 년 경력의 한국 전통 꿈 해몽 전문가입니다. ' 
                            '친절하고 신뢰감을 주는 어조로, 핵심 정보만 간결하게 설명해주세요.'
                        )
                    },
                    {
                        'role': 'user',
                        'content': (
                            f"{context}\n"
                            f"사용자의 꿈: {dream_input}\n"
                            "위 정보를 참고하여 200자 내외로 해몽을 작성해주세요."
                        )
                    }
                ]

                # 6) ChatCompletion 호출
                response = client.chat.completions.create(
                    model='gpt-3.5-turbo',
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                interpretation = response.choices[0].message.content

    return render(request, 'dreams/interpret.html', {
        'interpretation': interpretation,
        'error': error,
    })
