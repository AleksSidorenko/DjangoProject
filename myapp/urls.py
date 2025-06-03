from django.urls import path
from . import views


urlpatterns = [
   path('hello/', views.hello_alex, name='hello_alex'),
   path('', views.hello_alex, name='home'),
]
