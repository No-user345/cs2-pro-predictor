from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/favicon.png", permanent=True)
    ),

    path('', views.fantasy),
    path("fantasy-results/", views.fantasy_results),
]