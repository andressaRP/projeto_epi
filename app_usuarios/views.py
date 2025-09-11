from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Colaborador

# Create your views here.
def home(request):
    colaboradores = Colaborador.objects.all()
    return render(request, 'app_usuarios/pages/home.html') 

def index(request):
    colaboradores = Colaborador.objects.all()
    return render(request, 'app_usuarios/pages/index.html', {'colaboradores': colaboradores})   

def cadastrar_colaborador(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        matricula = request.POST.get('matricula', '').strip()
        if not nome or not cpf or not matricula:
            messages.error(request, "Todos os campos são obrigatórios.")
        elif Colaborador.objects.filter(cpf=cpf).exists():
            messages.error(request, "Já existe um colaborador com este CPF.")
        elif Colaborador.objects.filter(matricula=matricula).exists():
            messages.error(request, "Já existe um colaborador com esta matrícula.")
        else:
            try:
                Colaborador.objects.create(nome=nome, cpf=cpf, matricula=matricula)
                messages.success(request, "Colaborador cadastrado com sucesso!")
                return redirect('app_usuarios:index')  
            except Exception as e:
                messages.error(request, f"Erro ao salvar colaborador: {e}")

    return render(request, 'app_usuarios/pages/cadastrar.html', {'colaboradores': Colaborador.objects.all()})

def editar_colaborador(request, id):
    colaborador = Colaborador.objects.get(id=id)
    return render(request, 'app_usuarios/pages/update.html', {'colaborador': colaborador})

def update(request, id):
   try:
      colaborador = Colaborador.objects.get(pk=id) 
   except Colaborador.DoesNotExist:
      messages.error(request, "Colaborador não encontrado.")
      return redirect('app_usuarios:index')
   if request.method == 'POST':
      nome = request.POST.get('nome', '').strip()
      cpf = request.POST.get('cpf', '').strip()
      matricula = request.POST.get('matricula', '').strip()

      if not nome or not cpf or not matricula:
        messages.error(request, "Todos os campos são obrigatórios.")
      elif Colaborador.objects.filter(cpf=cpf).exclude(pk=colaborador.pk).exists():
        messages.error(request, "Já existe outro colaborador com este CPF.")
      elif Colaborador.objects.filter(matricula=matricula).exclude(pk=colaborador.pk).exists():
        messages.error(request, "Já existe outro colaborador com esta matrícula.")
      else:
        colaborador.nome = nome
        colaborador.cpf = cpf
        colaborador.matricula = matricula
        colaborador.save()
        messages.success(request, "Colaborador atualizado com sucesso!")
        return redirect('app_usuarios:index')
   return render(request, 'app_usuarios/pages/update.html', {'colaborador': colaborador})

def delete(request, id):
    colaborador = get_object_or_404(Colaborador, pk=id)
    if request.method == "POST":
     colaborador.delete()
     messages.success(request, f"Colaborador {colaborador.nome} excluído com sucesso!")
     return redirect("app_usuarios:index")
    else:
     return render(request, "app_usuarios/pages/confirmar_delete.html", {"colaborador": colaborador})