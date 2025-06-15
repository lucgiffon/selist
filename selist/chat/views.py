import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import TradeMessage, Trade, PrivateMessage, Conversation

User = get_user_model()


def main(request, conversation_id=None, recipient_id=None):
    current_conversation = None
    current_messages = []
    chat_title = "Agora"
    display_agora = True

    # Handle specific conversation views
    if conversation_id:  # trade or private conversation
        try:
            current_conversation = Conversation.objects.get(id=conversation_id)
            if current_conversation.conversation_type == "trade":
                current_messages = (
                    TradeMessage.objects.filter(trade=current_conversation.trade)
                    .select_related("trade", "user")
                    .order_by("created_at")
                )
                initial_message = current_conversation.trade.trademessage_set.filter(
                    type="initiation"
                ).first()
                chat_title = f"{current_conversation.trade.get_type_display()} - {initial_message.text}"
            elif current_conversation.conversation_type == "private":
                current_messages = (
                    PrivateMessage.objects.filter(conversation=current_conversation)
                    .select_related("conversation", "sender", "recipient")
                    .order_by("created_at")
                )
                other_participant = current_conversation.get_other_participant(
                    request.user
                )
                chat_title = f"Conversation avec {other_participant.username}"
            display_agora = False
        except Conversation.DoesNotExist:
            print("Conversation with id %s does not exist", conversation_id)
            raise Http404("La conversation demandée n'existe pas.")

    elif recipient_id:
        # Handle case where we want to start a private conversation
        try:
            recipient = User.objects.get(id=recipient_id)

            existing_conversation = (
                Conversation.objects.filter(
                    conversation_type="private", participants=request.user
                )
                .filter(participants=recipient)
                .first()
            )

            if existing_conversation:
                current_conversation = existing_conversation
                current_messages = (
                    PrivateMessage.objects.filter(conversation=current_conversation)
                    .select_related("conversation", "sender", "recipient")
                    .order_by("created_at")
                )
            chat_title = f"Conversation avec {recipient.username}"
            display_agora = False
        except User.DoesNotExist:
            print("User with id %s does not exist", recipient_id)
            raise Http404("La conversation demandée n'existe pas.")

    if display_agora:
        current_messages = (
            TradeMessage.objects.filter(type="initiation")
            .select_related("trade", "user")
            .all()
        )

    user_conversations = []

    if request.user.is_authenticated:
        user_conversations = (
            Conversation.objects.filter(participants=request.user)
            .prefetch_related("participants", "privatemessage_set")
            .select_related("trade")
            .order_by("-created_at")
        )

        user_conversations = sorted(
            user_conversations,
            key=lambda x: (
                x.get_last_message().created_at
                if x.get_last_message()
                else x.created_at
            ),
            reverse=True,
        )

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
            "current_messages": current_messages,
            "user_conversations": user_conversations,
            "current_conversation": current_conversation,
            "chat_title": chat_title,
            "agora_last_message": agora_last_message,
            "recipient_id": recipient_id,
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

        conversation = Conversation.objects.create(conversation_type="trade")
        conversation.participants.add(request.user)

        trade = Trade.objects.create(
            conversation=conversation, initiator=request.user, type=trade_type
        )

        message = TradeMessage.objects.create(
            text=message_text, user=request.user, trade=trade, type="initiation"
        )

        return JsonResponse(
            {
                "success": True,
                "conversation_id": conversation.id,
                "message_id": message.id,
            }
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
        conversation_type = data.get("conversation_type")
        conversation_id = data.get("conversation_id")
        recipient_id = data.get("recipient_id")

        if not message_text:
            return JsonResponse({"error": "Message text is required"}, status=400)

        if conversation_type == "trade":
            if not conversation_id:
                return JsonResponse(
                    {"error": "Conversation ID is required"}, status=400
                )

            try:
                conversation = Conversation.objects.get(
                    id=conversation_id, conversation_type="trade"
                )
                trade = conversation.trade
            except Conversation.DoesNotExist:
                return JsonResponse(
                    {"error": "Trade conversation not found"}, status=404
                )

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

        elif conversation_type == "private":
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(
                        id=conversation_id, conversation_type="private"
                    )
                    recipient = conversation.get_other_participant(request.user)
                except Conversation.DoesNotExist:
                    return JsonResponse(
                        {"error": "Private conversation not found"}, status=404
                    )
            elif recipient_id:
                try:
                    recipient = User.objects.get(id=recipient_id)

                    conversation = (
                        Conversation.objects.filter(
                            conversation_type="private", participants=request.user
                        )
                        .filter(participants=recipient)
                        .first()
                    )

                    if not conversation:
                        conversation = Conversation.objects.create(
                            conversation_type="private"
                        )
                        conversation.participants.add(request.user, recipient)

                except User.DoesNotExist:
                    return JsonResponse({"error": "Recipient not found"}, status=404)
            else:
                return JsonResponse(
                    {"error": "Conversation ID or recipient ID is required"}, status=400
                )

            message = PrivateMessage.objects.create(
                text=message_text,
                sender=request.user,
                recipient=recipient,
                conversation=conversation,
            )

            return JsonResponse(
                {
                    "success": True,
                    "message_id": message.id,
                    "message_text": message.text,
                    "message_time": message.created_at.strftime("%d-%m-%Y | %H:%M"),
                    "user_name": message.sender.username,
                    "conversation_id": conversation.id,
                }
            )

        else:
            return JsonResponse({"error": "Invalid conversation type"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
