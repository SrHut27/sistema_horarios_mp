from django import forms
from django.contrib import admin
from .models import DiaDaSemana, Hora, Professor, Turma, Aluno, Aula, CargaHorariaProfessor, CargaHorariaTurma
from django.contrib.auth.models import User

class CustomModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar as horas cronologicamente
        self.fields['horas'].queryset = Hora.objects.order_by('horario')

@admin.register(CargaHorariaProfessor)
class CargaHorariaProfessorAdmin(admin.ModelAdmin):
    list_display = ('professor', 'dia_semana', 'listar_horas')
    filter_horizontal = ('horas',)
    list_filter = ('professor', 'dia_semana')
    form = CustomModelForm

    def listar_horas(self, obj):
        # Ordenar as horas na exibição
        horas_ordenadas = obj.horas.all().order_by('horario')
        return ", ".join([str(hora) for hora in horas_ordenadas])

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by('professor__nome', 'dia_semana__id', 'id')
        return queryset

@admin.register(CargaHorariaTurma)
class CargaHorariaTurmaAdmin(admin.ModelAdmin):
    list_display = ('turma', 'dia_semana', 'listar_horas')
    filter_horizontal = ('horas',)
    list_filter = ('turma', 'dia_semana')
    form = CustomModelForm

    def listar_horas(self, obj):
        # Ordenar as horas na exibição
        horas_ordenadas = obj.horas.all().order_by('horario')
        return ", ".join([str(hora) for hora in horas_ordenadas])

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by('turma__nome', 'dia_semana__id', 'id')
        return queryset

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dia_semana', 'hora', 'professor', 'turma', 'criado_por', 'data_criacao')
    list_filter = ('dia_semana', 'hora', 'professor', 'turma')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by('-data_criacao')  # Ordena por data de criação descendente
        return queryset
    
    def save_model(self, request, obj, form, change):
        # Atribuir o usuário logado como criador da aula
        obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'listar_turmas')

    def listar_turmas(self, obj):
        return ", ".join([turma.nome for turma in obj.turmas.all()])

    listar_turmas.short_description = "Turmas"  # Define o cabeçalho da coluna

@admin.register(Hora)
class HoraAdmin(admin.ModelAdmin):
    list_display = ('horario',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by('horario')
        return queryset


admin.site.register(Professor)
admin.site.register(Turma)
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(DiaDaSemana)
