from django.urls import path, include    
from django.conf import settings
from django.conf.urls.static import static
from sistema.views import  create_systems, horarios_view, sistema_view, create_varios_sistemas, login_view, cadastro_view, listar_alunos_view, listar_professores_view, listar_turmas_view, ultimas_aulas_view, create_systems_completo, confirmacao_conflito, vizualizar_turmas_view, excluir_aula
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    path('', horarios_view, name= 'horarios_view'),
    path('cad/', create_systems, name='create_systems'),
    path('cadvarios/', create_varios_sistemas, name='create_varios_sistemas'),
    path('sistema/', sistema_view, name = 'sistema_view'),
    path('listaralunos/', listar_alunos_view, name = 'listar_alunos_view'),
    path('listarturmas/', listar_turmas_view, name = 'listar_turmas_view'),
    path('listarprofessores/', listar_professores_view, name = 'listar_professores_view'),
    path('ultimasaulas/', ultimas_aulas_view, name = 'ultimas_aulas_view'),
    path('excluir-aula/<int:aula_id>/', excluir_aula, name='excluir_aula'),
    path('cadcompleto/', create_systems_completo, name='create_systems_completo'),
    path('confirmacao_conflito/<str:nome_aula>/<int:turma_id>/<int:professor_id>/<int:dia_escolhido>/<int:hora_escolhida>/', confirmacao_conflito, name='confirmacao_conflito'),    
    path('login/', login_view, name='login_view'),
    path('mp30233106/', cadastro_view, name='cadastro_view'),
    path('aulas_turmas_horas/', vizualizar_turmas_view, name='vizualizar_turmas_view'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login_view'),
     # URL para deslogar o usuário
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

     # URL para solicitar a redefinição de senha
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),

    # URL para a página de confirmação de envio do email de redefinição de senha
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # URL para confirmar a redefinição de senha
    path('reset_password_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # URL para a página de sucesso de redefinição de senha
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)