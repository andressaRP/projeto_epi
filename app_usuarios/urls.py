from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from . import views
app_name = 'app_usuarios' 

urlpatterns = [
    path('registrar/', views.registrar, name='registrar'), # rota para registrar usuário
    
    path('', login_required(views.home), name='home'),
    path('index/', login_required(views.index), name='index'),
    path('cadastrar_colaborador/', login_required(views.cadastrar_colaborador), name='cadastrar_colaborador'),
    path('editar_colaborador/<int:id>/', login_required(views.editar_colaborador), name='editar_colaborador'),
    path('update/<int:id>/', login_required(views.update), name='update'),
    path('delete/<int:id>/', login_required(views.delete), name='delete'),
]