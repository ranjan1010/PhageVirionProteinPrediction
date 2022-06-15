from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submission/', views.submission, name='submission'),
    path('help/', views.help, name='help'),
    path('team/', views.team, name='team'),
    path('contact/', views.contact, name='contact'),
    path('submission/prediction', views.prediction, name='prediction')
]