from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from chat.models import TradeMessage, Trade
from .forms import SelisteCreationForm
from .models import Seliste


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


@login_required
def profile_view(request, user_id):
    profile_user = get_object_or_404(Seliste, id=user_id)

    show_initiator_only = request.GET.get("initiator_only") == "1"
    trade_type_filter = request.GET.get("trade_type", "both")

    user_trades_query = Trade.objects.filter(trademessage__user=profile_user).distinct()

    if show_initiator_only:
        user_trades_query = user_trades_query.filter(initiator=profile_user)

    if trade_type_filter in ["offer", "demand"]:
        user_trades_query = user_trades_query.filter(type=trade_type_filter)

    user_trades = []
    for trade in user_trades_query:
        last_user_message = (
            TradeMessage.objects.filter(trade=trade, user=profile_user)
            .order_by("-created_at")
            .first()
        )

        if last_user_message:
            user_trades.append(
                {
                    "trade": trade,
                    "last_message_date": last_user_message.created_at,
                    "is_initiator": trade.initiator == profile_user,
                }
            )

    user_trades.sort(key=lambda x: x["last_message_date"], reverse=True)

    paginator = Paginator(user_trades, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "show_initiator_only": show_initiator_only,
        "trade_type_filter": trade_type_filter,
    }

    return render(request, "users/profile.html", context)
