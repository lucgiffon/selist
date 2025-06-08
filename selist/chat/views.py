from django.shortcuts import render

from users.models import Seliste
from .models import Message
from .models import Trade


def main(request):
    initiation_messages = (
        Message.objects.filter(type="initiation").select_related("trade", "user").all()
    )
    print(initiation_messages)
    return render(
        request, "chat/main.html", {"initiation_messages": initiation_messages}
    )
