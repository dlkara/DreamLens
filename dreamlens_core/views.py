from django.shortcuts import render
from .forms import DreamForm

# FAISS 검색 및 LLM 응답 생성 로직 가져오기
from utils.faiss_helper import load_faiss_index, search_similar_dreams
from utils.generator import generate_interpretation

def index(request):
    if request.method == 'POST':
        form = DreamForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data['dream']
            index, meta = load_faiss_index()
            similar = search_similar_dreams(user_input, index, meta)
            result = generate_interpretation(user_input, similar)
            return render(request, 'dreamlens_core/result.html', {
                'user_input': user_input,
                'similar': similar,
                'result': result,
            })
    else:
        form = DreamForm()
    return render(request, 'dreamlens_core/index.html', {'form': form})


def result(request):
    return render(request, 'dreamlens_core/result.html')
