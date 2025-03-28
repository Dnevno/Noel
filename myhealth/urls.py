from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('register/doctor', views.register_doctor, name='register_doctor'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('dashboard/<int:username>', views.dashboard, name="dashboard"),
    path('testing/', views.testing, name='testing'),
]