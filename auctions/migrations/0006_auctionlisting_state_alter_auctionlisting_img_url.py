# Generated by Django 5.1.3 on 2024-12-08 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_rename_name_auctionlisting_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionlisting',
            name='state',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='auctionlisting',
            name='img_url',
            field=models.URLField(blank=True),
        ),
    ]