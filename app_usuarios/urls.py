from django.contrib import admin
from django.urls import path, include
from . import views
app_name = 'app_usuarios' 

urlpatterns = [
    path('', views.home, name='home'),
    path('index/', views.index, name='index'),
    path('cadastrar_colaborador/', views.cadastrar_colaborador, name='cadastrar_colaborador'),
    path('editar_colaborador/<int:id>/', views.editar_colaborador, name='editar_colaborador'),
    path('update/<int:id>/', views.update, name='update'),
    path('delete/<int:id>/', views.delete, name='delete'),
]