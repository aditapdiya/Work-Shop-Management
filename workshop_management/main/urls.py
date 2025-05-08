from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home_view, name='home'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='main/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='main/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='main/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='main/password_reset_complete.html'), name='password_reset_complete'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('workshops/', views.manage_workshops, name='manage_workshops'),
    path('workshops/add/', views.add_workshop, name='add_workshop'),
    path('workshops/edit/<int:id>/', views.edit_workshop, name='edit_workshop'),
    path('workshops/delete/<int:id>/', views.delete_workshop, name='delete_workshop'),
]

