from django.urls import path
from . import views


app_name = "main"

urlpatterns = [
    path("",views.HomeView.as_view(), name="home"),
    path("user_register/",views.user_data_view, name="user_register"),
    path("eva/<int:for_user_id>/",views.eva_view, name="eva"),
    path("status/", views.status_view, name="status"),
    path("status/radar_chart/", views.radar_chart_view, name="radar_chart"),
]