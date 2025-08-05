from django.urls import path
from . import views

urlpatterns = [
    # 메인 화면
    path('', views.index, name='index'),

    # 꿈 사전
    path('dict/', views.dream_dict_view, name='dream_dict_view'),

    # 꿈 조합기
    path('combine/', views.dream_combiner, name='dream_combiner'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_user, name='register_user'),
    path('check-username/', views.check_username, name='check_username'),

    path('mypage/', views.mypage, name='mypage'),

    path('interpret/', views.dream_interpreter, name='dream_interpreter'),
]
