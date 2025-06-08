from .forms import SelisteCreationForm
from django.shortcuts import render, redirect


def register_view(request):
    if request.method == "POST":
        form = SelisteCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/chat/")
    else:
        form = SelisteCreationForm()
    return render(request, "users/register.html", {"form": form})
