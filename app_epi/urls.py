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
from django.urls import path, include
from . import views
app_name = 'app_epi'

urlpatterns = [
    path('', views.home, name='home'),
    path('listar_epi/', views.listar_epi, name='listar_epi'),
    path('cadastrar_epi/', views.cadastrar_epi, name='cadastrar_epi'),
    path('editar_epi/<int:id>/', views.editar_epi, name='editar_epi'),
    path('update/<int:id>/', views.update, name='update'),
    path('pagina_editar_epi/', views.pagina_editar_epi, name='pagina_editar_epi'),
    path('delete/<int:id>/', views.delete, name='delete'),
    
]