from django.db import models


class Conversation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField("users.Seliste", related_name="conversations")
    conversation_type = models.CharField(
        max_length=10,
        choices=[
            ("trade", "Trade"),
            ("private", "Private"),
        ],
    )
    
    def get_last_message(self):
        if self.conversation_type == "trade" and hasattr(self, 'trade'):
            return self.trade.trademessage_set.order_by("-created_at").first()
        elif self.conversation_type == "private":
            return self.privatemessage_set.order_by("-created_at").first()
        return None
    
    def get_other_participant(self, current_user):
        return self.participants.exclude(id=current_user.id).first()
    
    def __str__(self):
        if self.conversation_type == "trade" and hasattr(self, 'trade'):
            return f"Trade: {self.trade.get_type_display()}"
        elif self.conversation_type == "private":
            participants = list(self.participants.all())
            if len(participants) >= 2:
                return f"Private: {participants[0].username} & {participants[1].username}"
        return f"Conversation ({self.conversation_type})"


class Trade(models.Model):
    conversation = models.OneToOneField("Conversation", on_delete=models.CASCADE, related_name="trade")
    initiator = models.ForeignKey(
        "users.Seliste", on_delete=models.PROTECT, related_name="initiated_trades"
    )
    type = models.CharField(
        max_length=6,
        choices=[
            ("offer", "Offre"),
            ("demand", "Demande"),
        ],
    )


class TradeMessage(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey("users.Seliste", on_delete=models.PROTECT)
    trade = models.ForeignKey("Trade", on_delete=models.PROTECT)
    type = models.CharField(
        max_length=12,
        choices=[
            ("initiation", "Initiation"),
            ("text", "Texte"),
            ("proposal", "Proposition"),
            ("finalisation", "Finalisation"),
        ],
    )

    def __str__(self):
        return self.text


class PrivateMessage(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey("users.Seliste", on_delete=models.PROTECT, related_name="sent_private_messages")
    recipient = models.ForeignKey("users.Seliste", on_delete=models.PROTECT, related_name="received_private_messages")
    conversation = models.ForeignKey("Conversation", on_delete=models.PROTECT)
    
    def __str__(self):
        return self.text


class Proposal(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        "users.Seliste", on_delete=models.PROTECT, related_name="sender"
    )
    receiver = models.ForeignKey(
        "users.Seliste", on_delete=models.PROTECT, related_name="receiver"
    )
    trade = models.ForeignKey("Trade", on_delete=models.PROTECT)
    value = models.IntegerField()
    accepted = models.BooleanField(default=False)


class Finalisation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    proposal = models.ForeignKey("Proposal", on_delete=models.PROTECT)
    accepted = models.BooleanField(default=False)
