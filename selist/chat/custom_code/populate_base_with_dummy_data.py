import os
import django
import sys
from django.db import transaction

sys.path.append("/home/lucgiffon/PycharmProjects/selist/selist")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "selist.settings")
django.setup()

from chat.models import Proposal, Finalisation, Trade, Message
from selist.models import Seliste

with transaction.atomic():

    seliste1 = Seliste.objects.create(username="seliste1")
    seliste2 = Seliste.objects.create(username="seliste2")

    trade1 = Trade.objects.create(initiator=seliste1, type="offer")
    trade2 = Trade.objects.create(initiator=seliste1, type="demand")
    trade3 = Trade.objects.create(initiator=seliste2, type="demand")

    message_trade1 = Message.objects.create(
        text="J'ai un peu de temps libre pour aider",
        user=seliste1,
        trade=trade1,
        type="initiation",
    )
    # message_trade1_proposition = Message.objects.create(
    #     "J'ai besoin d'aide pour tondre la pelouse" ,
    #     user_id=seliste2,
    #     trade_id=trade1,
    #     type="proposal",
    # )
    # message_trade1_finalisation = Message.objects.create(
    #     "Ca marche merci!" ,
    #     user_id=seliste1,
    #     trade_id=trade1,
    #     type="finalisation",
    # )
    #

    message_trade2 = Message.objects.create(
        text="J'ai besoin d'aide",
        user=seliste1,
        trade=trade1,
        type="initiation",
    )
    message_trade3 = Message.objects.create(
        text="J'ai besoin d'aide moi aussi",
        user=seliste2,
        trade=trade1,
        type="initiation",
    )
