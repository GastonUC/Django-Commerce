# Generated by Django 5.1.3 on 2024-12-07 21:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_rename_auctionlistings_auctionlisting_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionlisting',
            name='user',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='users', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]