from django.urls import path
from . import views

urlpatterns = [
    # 메인 화면
    path('', views.index, name='index'),

    # 꿈 해몽
    path('interpret/', views.dream_interpreter, name='dream_interpreter'),

    # 꿈 사전
    path('dict/', views.dream_dict, name='dream_dict'),

    # 꿈 조합기
    path('combine/', views.dream_combiner, name='dream_combiner'),

    # 꿈 일기장 -> TODO : 현정
    path('diary-list/', views.diary_list, name='diary_list'),
    path('diary/<int:year>-<int:month>-<int:day>/', views.diary_detail, name='diary-detail'),
    
    # 분석 리포트 -> TODO : 지우
    path('report/', views.report, name='report'),

    # 로그인/로그아웃, 회원가입
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # 마이페이지
    path('mypage/', views.mypage_view, name='mypage'),
]
