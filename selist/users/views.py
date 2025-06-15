from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404

from chat.models import TradeMessage, Conversation
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

    trade_conversations_query = Conversation.objects.filter(
        conversation_type="trade",
        participants=profile_user
    ).select_related("trade").prefetch_related("trade__trademessage_set")

    if show_initiator_only:
        trade_conversations_query = trade_conversations_query.filter(trade__initiator=profile_user)

    if trade_type_filter in ["offer", "demand"]:
        trade_conversations_query = trade_conversations_query.filter(trade__type=trade_type_filter)

    user_trades = []
    for conversation in trade_conversations_query:
        trade = conversation.trade
        last_user_message = (
            TradeMessage.objects.filter(trade=trade, user=profile_user)
            .order_by("-created_at")
            .first()
        )

        if last_user_message:
            user_trades.append(
                {
                    "trade": trade,
                    "conversation": conversation,
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
