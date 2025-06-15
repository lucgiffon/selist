from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.main, name="main"),
    path("conversation/<int:conversation_id>/", views.main, name="conversation"),
    path("start-private/<int:recipient_id>/", views.main, name="start_private"),
    path("create-trade/", views.create_trade, name="create_trade"),
    path("send-message/", views.send_message, name="send_message"),
]
