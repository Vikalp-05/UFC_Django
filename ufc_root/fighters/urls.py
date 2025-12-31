from django.urls import path
from . import views

urlpatterns = [
    path("", views.weightclass_list, name="weightclass_list"),
    path("weight-class/<slug:slug>/", views.weightclass_detail, name="weightclass_detail"),
    path("fighter/<slug:slug>/", views.fighter_detail, name="fighter_detail"),
]