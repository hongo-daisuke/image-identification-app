from django.urls import path
from . import views

app_name = 'identification'

urlpatterns = [
    path('', views.IdentificationIndexView.as_view(), name='index'),
    path('result/', views.IdentificationResultView.as_view(), name='result')
]
