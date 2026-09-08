from django.urls import path
from . import views

urlpatterns = [
    path('', views.fantasy),
    path("fantasy-results/", views.fantasy_results),
]