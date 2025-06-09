from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.main),
    path("create-trade/", views.create_trade, name="create_trade"),
]
