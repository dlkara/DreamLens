from django.urls import path
from . import views

urlpatterns = [

    # 꿈 조합기 페이지
    path('combine/', views.dream_combiner, name='dream_combiner'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
