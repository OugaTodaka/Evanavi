from django.shortcuts import render
from django.views.generic import *
from .models import Eva

class HomeView(ListView):
    model = Eva
    template_name = "main/home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context