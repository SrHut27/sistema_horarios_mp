# Generated by Django 5.0.2 on 2024-02-29 14:42

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0007_remove_aula_created_at_remove_aula_created_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='aula',
            name='criado_por',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='aula',
            name='data_criacao',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True),
        ),
    ]