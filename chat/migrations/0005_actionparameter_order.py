# Generated by Django 5.0.4 on 2024-04-30 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_delete_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionparameter',
            name='order',
            field=models.IntegerField(default=1),
        ),
    ]
