from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [
    path('signup/',
    views.SignUpView.as_view(),
    name='signup'),

    path('signup_success/',
    views.SignUpSuccessView.as_view(),
    name='signup_success'),
    
    path('login/', views.LoginView.as_view(), name="signin"),
]