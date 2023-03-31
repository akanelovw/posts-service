# Generated by Django 2.2.16 on 2023-03-31 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_follow'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_subscription'),
        ),
    ]