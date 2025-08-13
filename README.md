# DreamLens — AI 꿈 해몽 & 꿈 일기 분석
사용자가 기록한 꿈을 LLM으로 해석하고, 감정/종류/키워드 빈도를 리포트로 시각화하는 Django 기반 웹앱입니다.  
한국어 우선, KST(Asia/Seoul) 기준으로 동작합니다.



## 프로젝트 소개
_**“당신의 꿈, 우리는 그 속의 이야기를 읽습니다.”**_

우리는 ‘무의식의 이야기’를 기술로 들여다보는 팀, 김이안연구소입니다.

"DreamLens"는 인간의 꿈이라는 주관적이고 몽환적인 경험을 **AI 기반 해석 시스템**으로 풀어내고자 하는 프로젝트입니다.

팀 김이안연구소는 데이터 분석, 웹 개발, UI/UX 기획, 인공지능 분야의 경험을 바탕으로, 사용자들이 기록한 꿈을 **의미 기반으로 분석**하고, 이를 통해 **심리적 통찰과 자기 이해**로 이어지는 경험을 제공합니다.

우리는 단순한 ‘해몽 앱’을 넘어, 꿈이라는 감정과 기억의 조각들을 **언어로, 데이터로, 이야기로** 풀어내는 감성적 도구를 지향합니다.

기술은 날카롭되, 결과는 따뜻하게.

**DreamLens는 그 렌즈의 시작입니다.**



## 주요 기능
- **AI 해몽:** 입력한 꿈 텍스트를 LLM으로 분석·요약·해석
- **유사 꿈 검색 (옵션):** FAISS 인덱스로 의미기반 유사 사례 조회
- **꿈 일기장:** 일별 기록/조회, 월간 네비게이션
- **리포트:** 감정 분포, 꿈 종류 분석, 키워드 워드클라우드
- **모바일 우선 UI:** 간결한 탭/카드형 구성 (다크 모드 선택 가능)


## 팀 구성 및 역할

| **팀원**       | **기획**                 | **구현**                       | **공동 기여·협업**                |
| ------------ | ---------------------- | ---------------------------- | --------------------------- |
| **이현정 (팀장)** | 스토리보드 작성, 서비스 흐름 정립    | 꿈 조합기 LLM·페이지, 분석 리포트, 공통 헤더 | 배포, 일정 관리, Git·Notion·문서 관리 |
| **김지우**      | 꿈 사전 데이터 수집, AI 처리 흐름도 | 해몽 LLM·페이지, 꿈 일기장            | —                           |
| **안주경**      | ERD 설계, 페이지 구성·화면 흐름   | 로그인·회원가입, 페이지 접근 제어          | 전체 CSS 스타일링                 |


## Skills & Tools

### 🖥 Backend & Web Framework
| **기술 / 도구**                     | **설명**                             |
|------------------------------------|--------------------------------------|
| Django                             | 사용자 인증, 일기장 저장, 서버 사이드 로직 구현 |
| Streamlit *(옵션, 프로토타입/데모)* | LLM 기반 해몽 분석 데모 UI 구현        |
| HTML / CSS                         | 기본 UI 구조 및 스타일링                 |
| Django Template Filter             | 커스텀 템플릿 필터(`dict_get`) 작성        |

### 💻 Language & Libraries
| **기술 / 도구**                   | **설명**                                   |
|----------------------------------|--------------------------------------------|
| Python                           | 전체 로직 및 API 통신, 데이터 처리                  |
| Requests, JSON, NumPy, dotenv    | API 통신, JSON 처리, 배열 연산, 환경 변수 관리       |
| BeautifulSoup                    | 꿈 사전 등 외부 데이터 크롤링용 HTML 파서            |

### 🤖 AI 활용 및 LLM 연동
| **기술 / 도구**          | **설명**                          |
|-------------------------|-----------------------------------|
| OpenAI GPT-4o API       | 자연어 기반 해몽 생성, 감정 분석             |
| OpenAI Embedding API    | 꿈 텍스트 임베딩 벡터화 처리                |
| FAISS                   | 유사 꿈 사례 검색을 위한 벡터 인덱싱/검색      |
| LangChain (참조)        | 문서기반 질의응답 구조 설계 아이디어 참고       |
| Prompt Engineering      | GPT 응답 제어 프롬프트 최적화               |
| RAG 구조                | 벡터 검색 + 생성 기반 해석 구조 설계/구현      |

### 🗃 Database & 설계
| **기술 / 도구**                          | **설명**                         |
|------------------------------------------|----------------------------------|
| MySQL *(기본)* / SQLite *(개발용 옵션)*  | Django ORM 기반 모델/마이그레이션 |
| ERD Editor                               | ERD 기반 테이블 구조 설계          |

### 🔧 Tooling & 협업 환경
| **기술 / 도구**          | **설명**                    |
|-------------------------|-----------------------------|
| PyCharm                 | Python/Django 개발 환경       |
| Git & GitHub            | 버전 관리 및 협업               |
| Google Drive, Notion    | 자료 정리·일정 공유·문서 협업     |
| Draw.io                 | 시스템/화면 흐름 시각화          |
| 화면 흐름도 · 스토리보드 | 서비스 구조/페이지 연결성 기획     |



## 요구사항

- Python 3.11 ~ 3.13 권장



## 폴더 구조(예시)
```text
DreamLens/
├─ manage.py
├─ dreamlens_project/            # settings/urls/wsgi
├─ dreamlens_core/               # views/models/utils
├─ templates/                    # Django 템플릿
├─ static/
│  ├─ css/                       # common.css, header.css, report.css ...
│  └─ js/                        # header.js, report.js, diary-list.js ...
├─ data/
│  ├─ dream.json                 # 원본 꿈 사전(예시)
│  └─ meta_dream.json            # 메타데이터(유사 검색용)
├─ vectorDB/
│  └─ dream.index                # FAISS 인덱스
└─ utils/
   ├─ generator.py               # LLM 호출 로직
   └─ build_index.py             # (옵션) 인덱스 생성 스크립트
```

### 환경변수 (.env)

```text
# DB
DB_NAME=xxxxxx
DB_USER=xxxxxx
DB_PASSWORD=xxxxxx
DB_HOST=localhost
DB_PORT=3306


# API key
OPENAI_API_KEY=xxxxxx

LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=xxxxxx


# OAuth2 key
GOOGLE_CLIENT_ID=xxxxxx
GOOGLE_CLIENT_SECRET=xxxxxx

KAKAO_CLIENT_ID=xxxxxx

NAVER_CLIENT_ID=xxxxxx
NAVER_CLIENT_SECRET=xxxxxx
```

## 설치 및 실행

```bash
# 0) 가상환경
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

# 1) 의존성
pip install -r requirements.txt

# 2) DB 마이그레이션 & 어드민 생성
python manage.py migrate
python manage.py createsuperuser

# 3) (옵션) FAISS 인덱스 생성
python utils/build_index.py  # 스크립트가 있을 경우

# 4) 개발 서버
python manage.py runserver
```

## 사용 흐름

- (선택) 로그인 → 꿈 텍스트 입력 → AI 해몽 결과 확인/저장

- 월간 일기장 탐색 → 리포트(감정/종류/키워드) 확인

## 정적 파일 배포

```bash
# DEBUG=false 환경에서
python manage.py collectstatic --clear --noinput
# Whitenoise 또는 웹서버(Nginx/S3 등) 정적 서빙 설정 필요
```

## 데이터 준비

- vectorDB/dream.index & data/meta_dream.json → DreamInterpretTest 실행 시 생성

- data/dream.json → crawling/data_crawl.ipynb 실행 시 생성



### setting.py 설정 (발췌)
```python
# settings.py
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # 배포 시 collectstatic 타깃

# 배포 시 반드시 도메인 반영
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'your-domain.com']
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
```

### .gitignore 설정 (권장)
```text
.env
__pycache__/
staticfiles/
vectorDB/
data/
*.log
```



## Troubleshooting

| 오류 메시지                                                                                                        | 문제점                                                        | 해결방안                                                                |
| ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------- |
| `RuntimeWarning: DateTimeField Diary.date received a naive datetime (...) while time zone support is active.` | 타임존 활성화 상태에서 naive datetime 저장                             | `USE_TZ=True` 유지, 저장 전 `timezone.make_aware()`로 변환                  |
| `GET /static/... 500`                                                                                         | `DEBUG=False`에서 정적 경로/수집/서빙 미설정                            | `STATIC_ROOT` 지정, `collectstatic` 실행, Whitenoise/웹서버 정적 설정 및 퍼미션 확인 |
| `pip ... numpy 2.3.2 incompatible with opencv-python ...`                                                     | Numpy/Opencv 버전 충돌                                         | `pip install "numpy<2.3.0"` 또는 opencv 버전 고정(둘 중 하나 기준 맞춤)           |
| `NameError at /report/ name 'Max' is not defined`                                                             | Python 오탈자(`Max`)                                          | 내장함수 `max()`로 수정 또는 필요한 모듈 정확히 import                               |
| `NoReverseMatch ... 'diary_list_yyyymm' not found`                                                            | URL name 불일치                                               | `urls.py`의 `name`과 템플릿 `{% url %}` 이름 통일                            |
| `KeyError 'title' (generator.py)`                                                                             | 요청 데이터 키 누락/명칭 불일치                                         | `request.POST.get('title')`로 방어, 폼 필드 `name` 점검, None 처리 로직 추가      |
| 인덱스/메타 로드 실패                                                                                                  | `vectorDB/dream.index` 또는 `data/meta_dream.json` 부재/경로 불일치 | 인덱스 재생성, 상수 경로(INDEX\_PATH/METADATA\_PATH)와 실제 파일 일치 확인             |
| 정적 변경 미반영                                                                                                     | 브라우저/프록시 캐시                                                | 강력 새로고침, 파일명 해시 또는 `?v=YYYYMMDDHH` 쿼리로 캐싱 무효화                       |



## 보안
- API 키·비밀키는 .env로 관리(절대 커밋 금지)
- 사용자 데이터 백업/삭제 정책 수립 권장

## 라이선스
내부 프로젝트(비공개). **제3자 재배포 금지.**
