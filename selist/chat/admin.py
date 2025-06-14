from django.contrib import admin

from .models import Proposal, Finalisation, Trade, TradeMessage

# Register your models here.
admin.site.register(Proposal)
admin.site.register(TradeMessage)
admin.site.register(Finalisation)
admin.site.register(Trade)
