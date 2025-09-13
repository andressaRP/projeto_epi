from django.urls import path
from . import views

app_name = "app_emprestimos"

urlpatterns = [
    path("", views.listar, name="listar"),                # lista com busca/filtros
    path("novo/", views.cadastrar, name="cadastrar"),     # formulário simples
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("colaboradores/", views.painel_colaboradores, name="painel_colaboradores"),  # visão por colaborador com contagem
]
