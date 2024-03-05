from django.contrib.auth import login
from django.contrib.auth.decorators import login_required 
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .models import Aula, Professor, Turma, DiaDaSemana, Hora, CargaHorariaProfessor, CargaHorariaTurma, Aluno
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import random 
from .utilis import validar_conflito_turma, validar_conflito_aluno, tem_conflito_turma, tem_conflito_aluno
from django.http import HttpResponse

@staff_member_required(login_url = 'login_view')
def ultimas_aulas_view(request):
    ultimas_aulas = Aula.objects.all().order_by('-id')[:20]

    context = {
        'ultimas_aulas': ultimas_aulas
    }

    return render(request, 'ultimas_aulas.html', context)

from django.forms import ValidationError

@staff_member_required(login_url='login_view')
def create_systems_completo(request):
    if request.method == 'POST':
        nome_aula_id = request.POST.get('nome_aula_id')
        turma_id = request.POST.get('turma_id')
        professor_id = request.POST.get('professor_id')
        dia_escolhido = request.POST.get('dia_escolhido')
        hora_escolhida = request.POST.get('hora_escolhida')

        turma = Turma.objects.get(id=turma_id)
        professor = Professor.objects.get(id=professor_id)
        dia_da_semana_instance = DiaDaSemana.objects.get(id=dia_escolhido)
        hora_escolhida_instance = Hora.objects.get(id=hora_escolhida)

        # Verificar se há conflitos de horário para a turma ou de alunos
        conflito_turma = tem_conflito_turma(dia_da_semana_instance, hora_escolhida_instance, turma)
        conflito_aluno = tem_conflito_aluno(dia_da_semana_instance, hora_escolhida_instance, turma)

        if conflito_turma or conflito_aluno:
            return redirect('confirmacao_conflito', nome_aula=nome_aula_id, turma_id=turma_id, professor_id=professor_id, dia_escolhido=dia_escolhido, hora_escolhida=hora_escolhida)
        else:
            nova_aula = Aula(nome=nome_aula_id, dia_semana=dia_da_semana_instance, hora=hora_escolhida_instance, professor=professor, turma=turma)
            # Passar as informações para o método clean do modelo Aula
            nova_aula.request = request
            try:
                nova_aula.clean()
            except ValidationError as e:
                messages.error(request, e)
                return redirect('create_systems_completo')
            else:
                nova_aula.criado_por = request.user
                nova_aula.save()
                messages.success(request, 'Aula criada com sucesso!')
                return redirect('create_systems_completo')

    else:
        # Renderizar a página de criação de aula
        turmas = Turma.objects.all()
        professores = Professor.objects.all()
        dias_semana = DiaDaSemana.objects.all()
        horas_disponiveis = Hora.objects.all()
        return render(request, 'cad_sistemas_completo.html', 
                      {'turmas': turmas, 
                       'professores': professores, 
                       'dias_semana': dias_semana, 
                       'horas_disponiveis': horas_disponiveis})



def confirmacao_conflito(request, nome_aula, turma_id, professor_id, dia_escolhido, hora_escolhida):
    if request.method == 'POST':
        if request.POST.get('confirmacao_conflito') == 'sim':
            # Se o usuário confirmar, salvar a aula e redirecionar para a página de criação de aula
            turma = Turma.objects.get(id=turma_id)
            professor = Professor.objects.get(id=professor_id)
            dia_da_semana_instance = DiaDaSemana.objects.get(id=dia_escolhido)
            hora_escolhida_instance = Hora.objects.get(id=hora_escolhida)
            
            nova_aula = Aula(nome=nome_aula, dia_semana=dia_da_semana_instance, hora=hora_escolhida_instance, professor=professor, turma=turma)
            nova_aula.criado_por = request.user
            nova_aula.save()
            messages.success(request, 'Aula criada com sucesso!')
            return redirect('create_systems_completo')
        else:
            # Se o usuário recusar, retornar uma mensagem indicando que a aula não foi cadastrada
            return HttpResponse("Aula não foi cadastrada.")
    else:
        tipo_conflito = "Já existe uma aula atribuída para essa turma ou para um ou mais alunos que pertencem a essa turma."
        return render(request, 'confirmacao_conflito.html', {'tipo_conflito': tipo_conflito})


@staff_member_required(login_url='login_view')
def create_systems(request):
    dia_escolhido = None
    hora_escolhida = None
    if request.method == 'POST':
        nome_aula = request.POST.get('nome_aula')
        turma_id = request.POST.get('turma')
        professor_id = request.POST.get('professor')

        turma = Turma.objects.get(id=turma_id)
        professor = Professor.objects.get(id=professor_id)

        # Pegando os dias da semana
        dias_semana = DiaDaSemana.objects.all()
        horas_disponiveis = Hora.objects.all()

        # Listando, para permitir combinações válidas
        combinacoes_validas = []

        last_validation_error = None  # Armazena o último erro de validação

        for dia in dias_semana:
            # Verificar se há carga horária definida para o professor e para a turma neste dia
            carga_horaria_professor = CargaHorariaProfessor.objects.filter(professor=professor, dia_semana=dia).exists()
            carga_horaria_turma = CargaHorariaTurma.objects.filter(turma=turma, dia_semana=dia).exists()
            if carga_horaria_professor and carga_horaria_turma:
                for hora in horas_disponiveis:
                    try:
                        # Tentar criar uma nova instância de Aula temporária para validar
                        nova_aula = Aula(nome=nome_aula, dia_semana=dia, hora=hora, professor=professor, turma=turma)
                        nova_aula.full_clean()  # Aplica todas as validações do modelo

                        # Validar conflito de turma para todos os objetos do loop
                        if validar_conflito_turma(dia, hora, turma):
                            raise ValidationError({'turma': 'Já existe uma aula para esta turma no mesmo dia e hora. Se deseja cadastrar uma subturma, por favor, vá para a aba "Cadastrar Aula Completo"'})

                        # Validar conflito de aluno para todos os objetos do loop
                        if validar_conflito_aluno(dia, hora, turma):
                            raise ValidationError({'aluno': 'Um ou mais alunos desta turma estão em outra aula no mesmo dia e hora.'})

                        # Se a validação for bem-sucedida, adicionar a combinação à lista de combinações válidas
                        combinacoes_validas.append((dia, hora))

                    except ValidationError as e:
                        # Armazenar apenas o último erro de validação
                        last_validation_error = {
                            'nome_aula': nome_aula,
                            'dia_semana': dia,
                            'hora': hora,
                            'professor': professor,
                            'turma': turma,
                            'errors': e.message_dict
                        }
                        continue
        # Se houver pelo menos uma combinação válida, escolher uma combinação aleatória
        if combinacoes_validas:
            # Escolher aleatoriamente uma combinação válida
            dia_escolhido, hora_escolhida = random.choice(combinacoes_validas)

            # Criar a aula com a combinação escolhida
            nova_aula = Aula(nome=nome_aula, dia_semana=dia_escolhido, hora=hora_escolhida, professor=professor, turma=turma)
            # Atribuir o usuário atualmente autenticado como criador da aula
            nova_aula.criado_por = request.user
            # Salvar a aula
            nova_aula.save()
            messages.success(request, 'Aula criada com sucesso!')
            # Se a aula for criada com sucesso, definir last_validation_error como None
            last_validation_error = None

        else:
            # Se nenhuma combinação válida for encontrada, exibir mensagem de erro
            messages.error(request, 'Não há combinação de dia e hora disponível. Verifique a Carga Horária do Professor ou da turma escolhida, ou se o professor já tem uma aula no horário escolhido')

        # Renderizar o formulário com o último erro de validação, se houver
        turmas = Turma.objects.all()
        professores = Professor.objects.all()
        context = {
            'turmas': turmas,
            'professores': professores,
            'last_validation_error': last_validation_error,
        }
        return render(request, 'cad_sistemas.html', context)

    else:
        # Se o método não for POST, renderizar o formulário
        turmas = Turma.objects.all()
        professores = Professor.objects.all()
        return render(request, 'cad_sistemas.html',
                      {'turmas': turmas, 'professores': professores})
   

@staff_member_required(login_url='login_view')
def create_varios_sistemas(request):
    if request.method == 'POST':
        nome_aula = request.POST.get('nome_aula')
        turma_id = request.POST.get('turma')
        professor_id = request.POST.get('professor')
        hora_id = request.POST.get('hora')

        turma = Turma.objects.get(id=turma_id)
        professor = Professor.objects.get(id=professor_id)
        hora = Hora.objects.get(id=hora_id)

        # Obter todos os dias da semana
        dias_semana = DiaDaSemana.objects.all()

        for dia in dias_semana:
            try:
                # Tentar criar uma nova instância de Aula temporária para validar
                nova_aula = Aula(nome=nome_aula, dia_semana=dia, hora=hora, professor=professor, turma=turma)
                # Atribuir o usuário atualmente autenticado como criador da aula
                nova_aula.criado_por = request.user
                nova_aula.full_clean()  # Aplica todas as validações do modelo
                
                # Verificar conflitos de turma
                if validar_conflito_turma(dia, hora, turma):
                    messages.error(request, 'Já existe uma aula para esta turma no mesmo dia e hora.')
                    break

                # Verificar conflitos de aluno
                if validar_conflito_aluno(dia, hora, turma):
                    messages.error(request, 'Um ou mais alunos desta turma estão em outra aula no mesmo dia e hora.')
                    break

                # Se a validação for bem-sucedida, criar a aula
                nova_aula.save()
                messages.success(request, f'Aula para {dia} criada com sucesso!')
            except ValidationError as e:
                error_messages = [str(error) for error in e]  # Convert each element to a string
                messages.error(request, f'Erro ao criar aula para {dia}: já existe aulas para esta combinação')

        return redirect('create_varios_sistemas')

    else:
        # Se o método não for POST, renderizar o formulário
        turmas = Turma.objects.all()
        professores = Professor.objects.all()
        horas = Hora.objects.all().order_by('horario')  # Ordenar as horas cronologicamente
        return render(request, 'cad_varios_sistemas.html', {'turmas': turmas, 'professores': professores, 'horas': horas})


##############################################################################################################################
@login_required(login_url = 'login_view')
def horarios_view(request):
    semanas = DiaDaSemana.objects.all()
    horas = Hora.objects.all().order_by('horario')
    termo_pesquisa = request.GET.get('termo_pesquisa', None)
    aluno_pesquisado = None
    professor_pesquisado = None
    turma_pesquisada = None
    aluno_turmas = None


    aulas_filtradas = Aula.objects.all()
    if termo_pesquisa:
        aluno_pesquisado = Aluno.objects.filter(nome__icontains=termo_pesquisa).first()
        professor_pesquisado = Professor.objects.filter(nome__icontains=termo_pesquisa).first()
        turma_pesquisada = Turma.objects.filter(nome__icontains=termo_pesquisa).first()

        if aluno_pesquisado:
            aulas_filtradas = aulas_filtradas.filter(turma__alunos=aluno_pesquisado)
            aluno_turmas = aluno_pesquisado.turmas.all()

        elif professor_pesquisado:
            aulas_filtradas = aulas_filtradas.filter(professor=professor_pesquisado)
        elif turma_pesquisada:
            aulas_filtradas = aulas_filtradas.filter(turma=turma_pesquisada)

    aulas_por_hora_semana = {}
    for hora in horas:
        aulas_por_semana = {}
        for semana in semanas:
            aula = aulas_filtradas.filter(hora=hora, dia_semana=semana).first()
            aulas_por_semana[semana] = aula
        aulas_por_hora_semana[hora] = aulas_por_semana

    context = {
        'semanas': semanas,
        'horas': horas,
        'aulas_por_hora_semana': aulas_por_hora_semana,
        'aluno_pesquisado': aluno_pesquisado,
        'professor_pesquisado': professor_pesquisado,
        'turma_pesquisada': turma_pesquisada,
        'termo_pesquisa': termo_pesquisa,
        'aluno_turmas': aluno_turmas,
    }

    return render(request, 'horarios.html', context)

@login_required(login_url='login_view')
def sistema_view(request):
    turmas = Turma.objects.all()
    turma_schedule_status = {}
    
    for turma in turmas:
        schedule_status = {}
        dias_semana_turma = turma.carga_horaria_semanal.all()

        for dia in dias_semana_turma:

            carga_horaria_turma = CargaHorariaTurma.objects.filter(turma=turma, dia_semana=dia).first()
            if not carga_horaria_turma:
                schedule_status[dia.nome] = 'Incomplete'
                continue

            horas_aula = carga_horaria_turma.horas.all()
            aulas_count = Aula.objects.filter(
                turma=turma,
                dia_semana=dia,
                hora__in=horas_aula
            ).count()

            if aulas_count == horas_aula.count():
                schedule_status[dia.nome] = 'Completo'
            else:
                schedule_status[dia.nome] = 'Precisa finalizar'


        turma_schedule_status[turma] = {
            'nome': turma.nome,
            'tutor': turma.tutor,
            'status': schedule_status,
        }

    return render(request, 'sistema.html', {'turma_schedule_status': turma_schedule_status})

@login_required(login_url='login_view')
def listar_alunos_view(request):
    termo_pesquisa = request.GET.get('termo_pesquisa')
    alunos = Aluno.objects.all()

    if termo_pesquisa:
        alunos = alunos.filter(nome__icontains=termo_pesquisa)

    return render(request, 'listar_alunos.html', {'alunos': alunos, 'termo_pesquisa': termo_pesquisa})

@login_required(login_url='login_view')
def listar_turmas_view(request):
    termo_pesquisa = request.GET.get('termo_pesquisa')
    turmas = Turma.objects.all()

    if termo_pesquisa:
        turmas = turmas.filter(nome__icontains=termo_pesquisa)

    return render(request, 'listar_turmas.html', {'turmas': turmas, 'termo_pesquisa': termo_pesquisa})

@login_required(login_url='login_view')
def listar_professores_view(request):
    termo_pesquisa = request.GET.get('termo_pesquisa')
    professores = Professor.objects.all()

    if termo_pesquisa:
        professores = professores.filter(nome__icontains=termo_pesquisa)

    return render(request, 'listar_professores.html', {'professores': professores, 'termo_pesquisa': termo_pesquisa})
###############################################################################################
def cadastro_view(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        user = User.objects.filter(username=username).first()

        if user:
            messages.error(request, 'Este username já está cadastrado')
            return redirect('cadastro_view')

        user = User.objects.create_user(username=username, email=email, password=senha)
        user.save()

        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('horarios_view')

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)

        if user:
            login(request, user)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('horarios_view')
        else:
            messages.error(request, 'Login inválido')
            return redirect('login_view')
