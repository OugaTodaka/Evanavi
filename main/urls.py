from django.urls import path
from . import views


app_name = "main"

urlpatterns = [
    path("",views.HomeView.as_view(), name="home"),
    path("user_register/",views.user_data_view, name="user_register"),
    path("eva/",views.eva_view, name="eva"),
    path("status/", views.status_view, name="status"),
    path("status/radar_chart/", views.radar_chart_view, name="radar_chart"),
    path("jobs/", views.job_list_view, name="job_list"),
    path("eva_list/", views.view_evaluation, name="eva_list"),
    path("generate/", views.generate_self_promotion, name="generate_self_promotion"),
    path('download_self_promotion/<str:format>/', views.download_self_promotion, name='download_self_promotion'),
]