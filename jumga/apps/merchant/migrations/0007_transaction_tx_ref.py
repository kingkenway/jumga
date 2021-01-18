# Generated by Django 3.1.4 on 2021-01-08 22:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0006_auto_20210107_0853'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='tx_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='merchant.payment'),
        ),
    ]