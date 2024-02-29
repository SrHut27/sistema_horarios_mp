from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils import timezone


class DiaDaSemana(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.nome

class Hora(models.Model):
    id = models.AutoField(primary_key=True)
    horario = models.TimeField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.horario.strftime('%H:%M')

class Professor(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    carga_horaria_semanal = models.ManyToManyField(
        DiaDaSemana, 
        through='CargaHorariaProfessor',
        related_name='carga_horaria_professores'
    )

    def __str__(self):
        return self.nome


class Turma(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    tutor = models.CharField(max_length=100, blank=True)
    carga_horaria_semanal = models.ManyToManyField(
        DiaDaSemana, 
        through='CargaHorariaTurma',
        related_name='carga_horaria_turmas'
    )
    @property
    def horarios_completos(self):
        for dia in self.carga_horaria_semanal.all():
            if not dia.aulas.exists():
                return False
        return True
    

    def __str__(self):
        return self.nome

class CargaHorariaProfessor(models.Model):
    id = models.AutoField(primary_key=True)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    dia_semana = models.ForeignKey(DiaDaSemana, on_delete=models.CASCADE)
    horas = models.ManyToManyField(Hora)

    def clean(self):
        # Verificar se já existe uma carga horária para o mesmo dia e professor
        if CargaHorariaProfessor.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana
        ).exclude(pk=self.pk).exists():
            raise ValidationError(_('Já existe uma carga horária para este professor neste dia.'))

    def __str__(self):
        return f'{self.professor.nome} - {self.dia_semana.nome}'

class CargaHorariaTurma(models.Model):
    id = models.AutoField(primary_key=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    dia_semana = models.ForeignKey(DiaDaSemana, on_delete=models.CASCADE)
    horas = models.ManyToManyField(Hora)

    def clean(self):
        # Verificar se já existe uma carga horária para o mesmo dia e turma
        if CargaHorariaTurma.objects.filter(
            turma=self.turma,
            dia_semana=self.dia_semana
        ).exclude(pk=self.pk).exists():
            raise ValidationError(_('Já existe uma carga horária para esta turma neste dia.'))

    def __str__(self):
        return f'{self.turma.nome} - {self.dia_semana.nome}'

class Aluno(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    turmas = models.ManyToManyField(Turma, related_name='alunos')

    def __str__(self):
        return self.nome

class Aula(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    dia_semana = models.ForeignKey(DiaDaSemana, on_delete=models.CASCADE)
    hora = models.ForeignKey(Hora, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, null=True)
    data_criacao = models.DateTimeField(default=timezone.now, editable=False, null=True)

    def save(self, *args, **kwargs):
        if not self.id:  # Se for uma nova instância
            user = None
            # Verifica se existe um usuário autenticado
            if hasattr(self, 'request') and hasattr(self.request, 'user'):
                user = self.request.user
            elif hasattr(self, 'user'):
                user = self.user
            # Define o usuário atual como criador
            if user and user.is_authenticated:
                self.criado_por = user
        super().save(*args, **kwargs)

    def clean(self):
        # Verificar se há carga horária definida para o dia da semana do professor
        if not CargaHorariaProfessor.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana
        ).exists():
            raise ValidationError(_('Não há carga horária definida para o professor {} neste dia da semana.').format(self.professor))
        

        # Verificar se há carga horária definida para o dia da semana da turma
        if not CargaHorariaTurma.objects.filter(
            turma=self.turma,
            dia_semana=self.dia_semana
        ).exists():
            raise ValidationError(_('Não há carga horária definida para a turma {} neste dia da semana.').format(self.turma))
        

        # Verificar se há conflito de horários para o professor
        if Aula.objects.filter(
            dia_semana=self.dia_semana,
            hora=self.hora,
            professor=self.professor
        ).exclude(pk=self.pk).exists():
            raise ValidationError(_('Este professor já tem outra aula marcada para este horário.'))
        

        # Verificar se há conflito de horários para a turma
        if Aula.objects.filter(
            dia_semana=self.dia_semana,
            hora=self.hora,
            turma=self.turma
        ).exclude(pk=self.pk).exists():
            raise ValidationError(_('Esta turma já tem outra aula marcada para este horário.'))
        

        # Verificar se há conflito de horários para os alunos
        alunos_na_turma = self.turma.alunos.all()
        turma = self.turma
        for aluno in alunos_na_turma:
            if Aula.objects.filter(
                dia_semana=self.dia_semana,
                hora=self.hora,
                turma__alunos=aluno
            ).exclude(pk=self.pk).exists():
                raise ValidationError(_('O aluno {} está em outra aula neste horário na turma {}.').format(aluno.nome, self.turma))

        # Verificar se a aula está dentro da carga horária do professor
        carga_horaria_professor = CargaHorariaProfessor.objects.filter(
            professor=self.professor,
            dia_semana=self.dia_semana
        ).first()
        if carga_horaria_professor:
            if not carga_horaria_professor.horas.filter(pk=self.hora.pk).exists():
                raise ValidationError(_('Esta aula está fora da carga horária do professor.'))

        # Verificar se a aula está dentro da carga horária da turma
        carga_horaria_turma = CargaHorariaTurma.objects.filter(
            turma=self.turma,
            dia_semana=self.dia_semana
        ).first()
        if carga_horaria_turma:
            if not carga_horaria_turma.horas.filter(pk=self.hora.pk).exists():
                raise ValidationError(_('Esta aula está fora da carga horária da turma.'))


    def __str__(self):
        return f'{self.nome} - {self.dia_semana} ({self.hora})'

    class Meta:
        unique_together = ('dia_semana', 'hora', 'professor', 'turma')
