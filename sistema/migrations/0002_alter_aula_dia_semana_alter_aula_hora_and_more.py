# Generated by Django 5.0.2 on 2024-02-19 01:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aula',
            name='dia_semana',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='sistema.diadasemana'),
        ),
        migrations.AlterField(
            model_name='aula',
            name='hora',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='sistema.hora'),
        ),
        migrations.AlterField(
            model_name='professor',
            name='carga_horaria_semanal',
            field=models.ManyToManyField(related_name='carga_horaria_professores', through='sistema.CargaHorariaProfessor', to='sistema.diadasemana'),
        ),
        migrations.AlterField(
            model_name='turma',
            name='carga_horaria_semanal',
            field=models.ManyToManyField(related_name='carga_horaria_turmas', through='sistema.CargaHorariaTurma', to='sistema.diadasemana'),
        ),
    ]
