from .forms import SelisteCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


def register_view(request):
    if request.method == "POST":
        form = SelisteCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/chat/")
    else:
        form = SelisteCreationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/chat/")
    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    return redirect("/chat/")
