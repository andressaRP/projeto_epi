"""
URL configuration for projeto_epi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from . import views
app_name = 'app_epi'

urlpatterns = [
    path('', login_required(views.home), name='home'),
    path('listar_epi/', login_required(views.listar_epi), name='listar_epi'),
    path('cadastrar_epi/', login_required(views.cadastrar_epi), name='cadastrar_epi'),
    path('editar_epi/<int:id>/', login_required(views.editar_epi), name='editar_epi'),
    path('update/<int:id>/', login_required(views.update), name='update'),
    path('delete/<int:id>/', login_required(views.delete), name='delete'),
    path('relatorio_epi/', login_required(views.relatorio_epi), name='relatorio_epi'), 
    
]