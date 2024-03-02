# utils.py

from .models import Aula

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