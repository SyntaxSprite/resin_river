from django.shortcuts import render

# Create your views here.

def startingpage(request):
    return render (request, 'resin_apps/index.html')