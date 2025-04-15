from django.contrib import admin

from .models import Proposal, Finalisation, Trade, Message

# Register your models here.
admin.site.register(Proposal)
admin.site.register(Message)
admin.site.register(Finalisation)
admin.site.register(Trade)
