from django.contrib import admin
from django.urls import path, include
from .views import home, cadastrar_colaborador, editar_colaborador, update, delete

urlpatterns = [
    path('', home, name='home'),
    path('cadastrar_colaborador/', cadastrar_colaborador, name='cadastrar_colaborador'),
    path('editar_colaborador/<int:id>/', editar_colaborador, name='editar_colaborador'),
    path('update/<int:id>/', update, name='update'),
    path('delete/<int:id>/', delete, name='delete'),
]