from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import models
import json

from .models import TradeMessage
from .models import Trade


def main(request, trade_id=None):
    # Get all initiation messages for the Agora (default view)
    if trade_id is None:
        initiation_messages = (
            TradeMessage.objects.filter(type="initiation")
            .select_related("trade", "user")
            .all()
        )
        current_trade = None
        chat_title = "Agora"
    else:
        # Get messages for specific trade conversation
        try:
            current_trade = Trade.objects.get(id=trade_id)
            initiation_messages = (
                TradeMessage.objects.filter(trade=current_trade)
                .select_related("trade", "user")
                .order_by("created_at")
            )
            chat_title = f"{current_trade.get_type_display()}"
        except Trade.DoesNotExist:
            # Fallback to Agora if trade doesn't exist
            initiation_messages = (
                TradeMessage.objects.filter(type="initiation")
                .select_related("trade", "user")
                .all()
            )
            current_trade = None
            chat_title = "Agora"

    # Get user's conversations if authenticated
    user_trades = []
    agora_last_message = None
    if request.user.is_authenticated:
        user_trades = (
            Trade.objects.filter(
                models.Q(initiator=request.user)
                | models.Q(trademessage__user=request.user)
            )
            .distinct()
            .select_related("initiator")
            .prefetch_related("trademessage_set")
            .order_by("-created_at")
        )

        # Get the last initiation message for Agora subtitle
        agora_last_message = (
            TradeMessage.objects.filter(type="initiation")
            .select_related("trade", "user")
            .order_by("-created_at")
            .first()
        )

    return render(
        request,
        "chat/main.html",
        {
            "initiation_messages": initiation_messages,
            "user_trades": user_trades,
            "current_trade": current_trade,
            "chat_title": chat_title,
            "agora_last_message": agora_last_message,
        },
    )


@csrf_exempt
@login_required
def create_trade(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        message_text = data.get("message", "").strip()
        trade_type = data.get("type", "")

        if not message_text:
            return JsonResponse({"error": "Message text is required"}, status=400)

        if trade_type not in ["offer", "demand"]:
            return JsonResponse({"error": "Invalid trade type"}, status=400)

        trade = Trade.objects.create(initiator=request.user, type=trade_type)

        message = TradeMessage.objects.create(
            text=message_text, user=request.user, trade=trade, type="initiation"
        )

        return JsonResponse(
            {"success": True, "trade_id": trade.id, "message_id": message.id}
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def send_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        message_text = data.get("message", "").strip()
        trade_id = data.get("trade_id")

        if not message_text:
            return JsonResponse({"error": "Message text is required"}, status=400)

        if not trade_id:
            return JsonResponse({"error": "Trade ID is required"}, status=400)

        try:
            trade = Trade.objects.get(id=trade_id)
        except Trade.DoesNotExist:
            return JsonResponse({"error": "Trade not found"}, status=404)

        message = TradeMessage.objects.create(
            text=message_text, user=request.user, trade=trade, type="text"
        )

        return JsonResponse(
            {
                "success": True,
                "message_id": message.id,
                "message_text": message.text,
                "message_time": message.created_at.strftime("%d-%m-%Y | %H:%M"),
                "user_name": message.user.username,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
