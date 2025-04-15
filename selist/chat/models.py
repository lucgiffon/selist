from django.db import models


class Message(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey("selist.Seliste", on_delete=models.PROTECT)
    trade = models.ForeignKey("Trade", on_delete=models.PROTECT)
    type = models.CharField(
        max_length=12,
        choices=[
            ("initiation", "Initiation"),
            ("text", "Texte"),
            ("proposal", "Proposition"),
            ("finalisation", "Finalisation"),
        ],
    )

    def __str__(self):
        return self.text


class Trade(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    initiator = models.ForeignKey(
        "selist.Seliste", on_delete=models.PROTECT, related_name="initiator"
    )
    type = models.CharField(
        max_length=6,
        choices=[
            ("offer", "Offre"),
            ("demand", "Demande"),
        ],
    )


class Proposal(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        "selist.Seliste", on_delete=models.PROTECT, related_name="sender"
    )
    receiver = models.ForeignKey(
        "selist.Seliste", on_delete=models.PROTECT, related_name="receiver"
    )
    value = models.IntegerField()
    accepted = models.BooleanField(default=False)


class Finalisation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)
    proposal = models.ForeignKey("Proposal", on_delete=models.PROTECT)
    accepted = models.BooleanField(default=False)
