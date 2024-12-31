# Generated by Django 5.1.4 on 2024-12-19 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_alter_auctionlisting_img_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(default='Explore this category!', max_length=100),
        ),
        migrations.AddField(
            model_name='category',
            name='img',
            field=models.URLField(default='https://placeholder.pics/svg/300/FBFFBC-C7FF63/000000-9BA6FF/example%20image'),
        ),
    ]