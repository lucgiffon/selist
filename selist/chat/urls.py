from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.main, name="main"),
    path("conversation/<int:trade_id>/", views.main, name="conversation"),
    path("create-trade/", views.create_trade, name="create_trade"),
    path("send-message/", views.send_message, name="send_message"),
]
