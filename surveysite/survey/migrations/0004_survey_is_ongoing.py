# Generated by Django 3.1 on 2020-08-28 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_auto_20200828_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='is_ongoing',
            field=models.BooleanField(default=False),
        ),
    ]
