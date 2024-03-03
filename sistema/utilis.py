# utils.py

from .models import Aula
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# utils.py


def validar_conflito_turma(dia, hora, turma):
    if Aula.objects.filter(
        dia_semana=dia,
        hora=hora,
        turma=turma
    ).exists():
        return True
    return False

def validar_conflito_aluno(dia, hora, turma):
    alunos_na_turma = turma.alunos.all()
    for aluno in alunos_na_turma:
        if Aula.objects.filter(
            dia_semana=dia,
            hora=hora,
            turma__alunos=aluno
        ).exists():
            return True
    return False

def tem_conflito_turma(dia_semana, hora, turma):
    return Aula.objects.filter(dia_semana=dia_semana, hora=hora, turma=turma).exists()

def tem_conflito_aluno(dia_semana, hora, turma):
    alunos_na_turma = turma.alunos.all()
    for aluno in alunos_na_turma:
        if Aula.objects.filter(dia_semana=dia_semana, hora=hora, turma__alunos=aluno).exists():
            return True
    return False