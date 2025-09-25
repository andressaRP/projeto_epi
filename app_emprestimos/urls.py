from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

app_name = "app_emprestimos"

urlpatterns = [
    path("", login_required(views.listar), name="listar"),                
    path("novo/", login_required(views.cadastrar), name="cadastrar"),    
    path("<int:pk>/editar/", login_required(views.editar), name="editar"),
    path("colaboradores/", login_required(views.painel_colaboradores), name="painel_colaboradores"),
    path('apagar/<int:pk>/', login_required(views.apagar), name='apagar'),
    path('relatorio/', views.relatorio, name='relatorio'),

    
]
