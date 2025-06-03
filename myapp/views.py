from django.shortcuts import render
from django.http import HttpResponse


def hello_alex(request):
   return HttpResponse("<h1>Hello, Alex</h1>")
