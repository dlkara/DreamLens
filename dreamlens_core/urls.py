from django.urls import path
from . import views

urlpatterns = [

    # 꿈 사전
    path('dict/', views.dream_dict_view, name='dream_dict_view'),

    # 꿈 조합기
    path('combine/', views.dream_combiner, name='dream_combiner'),
]
