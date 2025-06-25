from django.contrib import admin

from .models import (
    Proposal,
    Trade,
    TradeMessage,
    Conversation,
    PrivateMessage,
    Transaction,
)

# Register your models here.
admin.site.register(Proposal)
admin.site.register(TradeMessage)
admin.site.register(Trade)
admin.site.register(Conversation)
admin.site.register(PrivateMessage)
admin.site.register(Transaction)
