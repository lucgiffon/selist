from django.shortcuts import render


def homepage(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def offline(request):
    return render(request, "offline.html")
