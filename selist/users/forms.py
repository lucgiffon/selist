from django.contrib.auth.forms import UserCreationForm
from users.models import Seliste


class SelisteCreationForm(UserCreationForm):
    class Meta:
        model = Seliste
        fields = ("username",)
