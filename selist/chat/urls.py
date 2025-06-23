from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.main, name="main"),
    path("conversation/<int:conversation_id>/", views.main, name="conversation"),
    path("start-private/<int:recipient_id>/", views.main, name="start_private"),
    path("create-trade/", views.create_trade, name="create_trade"),
    path("send-message/", views.send_message, name="send_message"),
    path(
        "trade/<int:trade_id>/participants/",
        views.get_trade_participants,
        name="get_trade_participants",
    ),
    path("create-proposal/", views.create_proposal, name="create_proposal"),
    path("answer-proposal/", views.answer_proposal, name="answer_proposal"),
    path("direct-transfer/", views.direct_transfer, name="direct_transfer"),
]
