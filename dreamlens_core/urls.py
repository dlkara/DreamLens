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

    # 꿈 일기장 -> TODO : 현정, 지우
    path('diary/list/', views.diary_list, name='diary_list_base'),  # 기본 진입: today 리다이렉트
    path('diary/list/<int:yyyymm>', views.diary_list, name='diary_list'),
    path('diary/write/', views.diary_write, name='diary_write'),
    path('diary/writeOk/', views.diary_writeOk, name='diary_writeOk'),
    path('diary/detail/<int:pk>/', views.diary_detail, name='diary_detail'),
    path('diary/update/<int:pk>/', views.diary_update, name='diary_update'),
    path('diary/updateOk/', views.diary_updateOk, name='diary_updateOk'),
    path('diary/delete/<int:pk>/', views.diary_delete, name='diary_delete'),

    # 분석 리포트 -> TODO : 지우
    path('report/', views.report, name='report'),

    # 로그인/로그아웃, 회원가입
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register_user'),

    # 마이페이지
    path('check-username/', views.check_username, name='check_username'),

    path('mypage/', views.mypage, name='mypage'),
]
