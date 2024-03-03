from django.urls import path, include    
from django.conf import settings
from django.conf.urls.static import static
from sistema.views import  create_systems, horarios_view, sistema_view, create_varios_sistemas, login_view, cadastro_view, listar_alunos_view, listar_professores_view, listar_turmas_view, ultimas_aulas_view, create_systems_completo

urlpatterns = [
    path('', horarios_view, name= 'horarios_view'),
    path('cad/', create_systems, name='create_systems'),
    path('cadvarios/', create_varios_sistemas, name='create_varios_sistemas'),
    path('sistema/', sistema_view, name = 'sistema_view'),
    path('listaralunos/', listar_alunos_view, name = 'listar_alunos_view'),
    path('listarturmas/', listar_turmas_view, name = 'listar_turmas_view'),
    path('listarprofessores/', listar_professores_view, name = 'listar_professores_view'),
    path('ultimasaulas/', ultimas_aulas_view, name = 'ultimas_aulas_view'),
    path('cadcompleto/', create_systems_completo, name='create_systems_completo'),

    
    path('login/', login_view, name='login_view'),
    path('mp30233106/', cadastro_view, name='cadastro_view')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)