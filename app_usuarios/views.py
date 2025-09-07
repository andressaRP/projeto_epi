from django.shortcuts import render, redirect
from .models import Colaborador

# Create your views here.
def home(request):
    colaboradores = Colaborador.objects.all()
    return render(request, 'index.html', {'colaboradores': colaboradores})    

def cadastrar_colaborador(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        matricula = request.POST.get('matricula')
        colaborador = Colaborador(nome=nome, cpf=cpf, matricula=matricula)
        colaborador.save()
    return render(request, 'index.html', {'colaboradores': Colaborador.objects.all()})

def editar_colaborador(request, id):
    colaborador = Colaborador.objects.get(id=id)
    return render(request, 'update.html', {'colaborador': colaborador})

def update(request, id):
    colaborador = Colaborador.objects.get(id=id)
    colaborador.nome = request.POST.get('nome')
    colaborador.cpf = request.POST.get('cpf')
    colaborador.matricula = request.POST.get('matricula')
    colaborador.save()
    return redirect('home')

def delete(request, id):
    colaborador = Colaborador.objects.get(id=id)
    colaborador.delete()
    return redirect('home')