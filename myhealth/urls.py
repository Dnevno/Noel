from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('register/doctor', views.register_doctor, name='register_doctor'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification, name='resend_verification'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('dashboard/<int:user_id>', views.dashboard, name="dashboard"),
    path('testing/', views.testing, name='testing'),
]