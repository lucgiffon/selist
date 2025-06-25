import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .models import (
    TradeMessage,
    Trade,
    PrivateMessage,
    Conversation,
    Proposal,
    Transaction,
)

User = get_user_model()


def main(request, conversation_id=None, recipient_id=None):
    current_conversation = None
    current_messages = []
    chat_title = "Agora"
    display_agora = True

    if conversation_id:
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
                return redirect(
                    "chat:conversation", conversation_id=existing_conversation.id
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

    context = {
        "current_messages": current_messages,
        "user_conversations": user_conversations,
        "current_conversation": current_conversation,
        "chat_title": chat_title,
        "agora_last_message": agora_last_message,
        "recipient_id": recipient_id,
    }

    if display_agora:
        finalized_trades = set()
        cancelled_trades = set()
        for message in current_messages:
            if message.trade.status == "finalized":
                finalized_trades.add(message.trade.id)
            elif message.trade.status == "cancelled":
                cancelled_trades.add(message.trade.id)

        context["finalized_trades"] = finalized_trades
        context["cancelled_trades"] = cancelled_trades

    if current_conversation and current_conversation.conversation_type == "trade":
        context["current_trade"] = current_conversation.trade

        proposals = Proposal.objects.filter(
            trade=current_conversation.trade
        ).select_related("sender", "receiver", "trade_message")

        proposals_by_message = {}
        for proposal in proposals:
            if proposal.trade_message:
                proposals_by_message[proposal.trade_message.id] = proposal

        context["proposals_by_message"] = proposals_by_message

    return render(request, "chat/main.html", context)


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
                conversation.participants.add(request.user)
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


@csrf_exempt
@login_required
def get_trade_participants(request, trade_id):
    """Get participants of a trade (for recipient selection)"""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        trade = Trade.objects.get(id=trade_id)
        conversation = trade.conversation

        # Check if user is participant
        if not conversation.participants.filter(id=request.user.id).exists():
            return JsonResponse({"error": "Not authorized"}, status=403)

        participants = []
        for participant in conversation.participants.exclude(id=request.user.id):
            participants.append(
                {"id": participant.id, "username": participant.username}
            )

        return JsonResponse(
            {
                "success": True,
                "participants": participants,
                "trade_type": trade.type,
                "trade_initiator": trade.initiator.id,
            }
        )

    except Trade.DoesNotExist:
        return JsonResponse({"error": "Trade not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def create_proposal(request):
    """Create a proposal for a trade"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        trade_id = data.get("trade_id")
        amount = data.get("amount")
        other_user_id = data.get("other_user_id")

        if not all([trade_id, amount, other_user_id]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            amount = int(amount)
            if amount <= 0:
                return JsonResponse({"error": "Amount must be positive"}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid amount"}, status=400)

        trade = Trade.objects.get(id=trade_id)

        try:
            if trade.type == "offer":
                if request.user.id == trade.initiator.id:
                    sender_id = other_user_id
                    receiver_id = request.user.id
                else:
                    sender_id = request.user.id
                    receiver_id = other_user_id

                assert (
                    receiver_id == trade.initiator.id
                ), "Trade initiator must be the receiver in an offer"
            else:
                if request.user.id == trade.initiator.id:
                    sender_id = request.user.id
                    receiver_id = other_user_id
                else:
                    sender_id = other_user_id
                    receiver_id = request.user.id
                assert (
                    sender_id == trade.initiator.id
                ), "Trade initiator must be the sender in a demand"
        except AssertionError as e:
            return JsonResponse({"error": str(e)}, status=400)

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        if not trade.conversation.participants.filter(id=request.user.id).exists():
            return JsonResponse({"error": "Not authorized"}, status=403)

        if not trade.conversation.participants.filter(id=other_user_id).exists():
            return JsonResponse({"error": "Other user not in conversation"}, status=400)

        message_text = f"Proposition de {request.user.username} : {sender.username} envoie {amount} points à {receiver.username}"

        trade_message = TradeMessage.objects.create(
            text=message_text, user=request.user, trade=trade, type="proposal"
        )

        proposal = Proposal.objects.create(
            sender=sender,
            receiver=receiver,
            trade=trade,
            value=amount,
            trade_message=trade_message,
        )

        return JsonResponse(
            {
                "success": True,
                "message_id": trade_message.id,
                "proposal_id": proposal.id,
                "message_text": message_text,
                "message_time": trade_message.created_at.strftime("%d-%m-%Y | %H:%M"),
                "user_name": request.user.username,
            }
        )

    except Trade.DoesNotExist:
        return JsonResponse({"error": "Trade not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Recipient not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def answer_proposal(request):
    """Accept a proposal"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        proposal_id = data.get("proposal_id")

        if not proposal_id:
            return JsonResponse({"error": "Proposal ID is required"}, status=400)

        accepted = data.get("accepted")
        if accepted is None:
            return JsonResponse({"error": "Accepted field is required"}, status=400)

        proposal = Proposal.objects.get(id=proposal_id)

        if proposal.sender.id != request.user.id:
            return JsonResponse({"error": "Not authorized"}, status=403)

        if proposal.accepted or proposal.refused:
            return JsonResponse({"error": "Proposal already processed"}, status=400)

        if accepted is True:

            proposal.accepted = True
            proposal.save()

            payer = proposal.sender
            payee = proposal.receiver
            amount = proposal.value

            payer.value -= amount
            payee.value += amount
            payer.save()
            payee.save()

            transaction = Transaction.objects.create(
                sender=payer,
                recipient=payee,
                trade=proposal.trade,
                amount=amount,
                trade_message=proposal.trade_message,
            )

            finalization_text = f"Échange finalisé : {amount} points transférés de {payer.username} à {payee.username}"
            finalization_message = TradeMessage.objects.create(
                text=finalization_text,
                user=request.user,
                trade=proposal.trade,
                type="finalisation",
            )

            proposal.trade.status = "finalized"
            proposal.trade.save()

            return JsonResponse(
                {
                    "success": True,
                    "message_id": finalization_message.id,
                    "message_text": finalization_text,
                    "message_time": finalization_message.created_at.strftime(
                        "%d-%m-%Y | %H:%M"
                    ),
                    "user_name": request.user.username,
                    "transaction_id": transaction.id,
                }
            )
        else:
            proposal.refused = True
            proposal.save()

            return JsonResponse({"success": True, "message": "Proposition refusée"})

    except Proposal.DoesNotExist:
        return JsonResponse({"error": "Proposal not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def direct_transfer(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        trade_id = data.get("trade_id")
        amount = data.get("amount")
        recipient_id = data.get("recipient_id")

        if not all([trade_id, amount, recipient_id]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        try:
            amount = int(amount)
            if amount <= 0:
                return JsonResponse({"error": "Amount must be positive"}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid amount"}, status=400)

        trade = Trade.objects.get(id=trade_id)
        recipient = User.objects.get(id=recipient_id)

        # Check if user is participant
        if not trade.conversation.participants.filter(id=request.user.id).exists():
            return JsonResponse({"error": "Not authorized"}, status=403)

        # Check if recipient is participant
        if not trade.conversation.participants.filter(id=recipient.id).exists():
            return JsonResponse({"error": "Recipient not in conversation"}, status=400)

        # Transfer points
        sender = request.user
        sender.value -= amount
        recipient.value += amount
        sender.save()
        recipient.save()

        # Create finalization message
        finalization_text = f"Échange finalisé : {amount} points transférés de {sender.username} à {recipient.username}"
        finalization_message = TradeMessage.objects.create(
            text=finalization_text, user=request.user, trade=trade, type="finalisation"
        )

        trade.status = "finalized"
        trade.save()

        # Create transaction record
        transaction = Transaction.objects.create(
            sender=sender,
            recipient=recipient,
            trade=trade,
            amount=amount,
            trade_message=finalization_message,
        )

        return JsonResponse(
            {
                "success": True,
                "message_id": finalization_message.id,
                "message_text": finalization_text,
                "message_time": finalization_message.created_at.strftime(
                    "%d-%m-%Y | %H:%M"
                ),
                "user_name": request.user.username,
                "transaction_id": transaction.id,
            }
        )

    except Trade.DoesNotExist:
        return JsonResponse({"error": "Trade not found"}, status=404)
    except User.DoesNotExist:
        return JsonResponse({"error": "Recipient not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@login_required
def cancel_trade(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        trade_id = data.get("trade_id")

        if not trade_id:
            return JsonResponse(
                {"error": "Missing required field trade_id"}, status=400
            )

        trade = Trade.objects.get(id=trade_id)

        if not trade.initiator.id == request.user.id:
            return JsonResponse({"error": "Not authorized"}, status=403)

        trade.status = "cancelled"
        trade.save()

        return JsonResponse(
            {"success": True, "message": "Trade cancelled successfully"}
        )

    except Trade.DoesNotExist:
        return JsonResponse({"error": "Trade not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
