from django.urls import path
from . import views

urlpatterns = [

    # 꿈 조합기 페이지
    path('combine/', views.dream_combiner, name='dream_combiner'),
]
