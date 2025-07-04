# Generated by Django 5.1.6 on 2025-06-17 06:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chat", "0005_remove_trade_created_at_remove_trade_participants_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="proposal",
            name="refused",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="proposal",
            name="trade_message",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="chat.trademessage",
            ),
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("amount", models.IntegerField()),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="received_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="sent_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "trade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="chat.trade"
                    ),
                ),
                (
                    "trade_message",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="chat.trademessage",
                    ),
                ),
            ],
        ),
    ]
