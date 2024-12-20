# Generated by Django 5.1.3 on 2024-12-08 17:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auctionlisting_state_alter_auctionlisting_img_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.auctionlisting')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watchlist_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
