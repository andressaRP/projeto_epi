from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Epi

# Create your views here.
def home(request):
    epis = Epi.objects.all()
    return render(request, 'app_epi/pages/home.html')

def listar_epi(request):
    epis = Epi.objects.all()
    return render(request, 'app_epi/pages/lista.html', {'epis': epis})

def cadastrar_epi(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        codigo_interno = request.POST.get('codigo_interno', '').strip()
        ca = request.POST.get('ca', '').strip()
        tamanho = request.POST.get('tamanho', '').strip()
        vida_util_meses = request.POST.get('vida_util_meses', '').strip()    
        quantidade = request.POST.get('quantidade', '').strip()

        if not nome:
            messages.error(request, "O campo Nome é obrigatório.")
        else:
            epi = Epi(
                nome=nome,
                codigo_interno=codigo_interno or None,
                ca=ca or None,
                tamanho=tamanho or None,
                vida_util_meses=int(vida_util_meses) if vida_util_meses else None,
                quantidade=int(quantidade) if quantidade else 0,
            )
            epi.save()
            messages.success(request, "EPI cadastrado com sucesso!")
            return redirect("app_epi:cadastrar_epi") 

    return render(request, "app_epi/pages/cadastrar.html")

def editar_epi(request, id):
    epi = Epi.objects.get(id=id)
    return render(request, 'app_epi/pages/update.html', {'epi': epi})

def update(request, id):
    try:
        epi = Epi.objects.get(pk=id)
    except Epi.DoesNotExist:
        messages.error(request, "EPI não encontrado.")
        return redirect("app_epi:listar_epi")

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        codigo_interno = request.POST.get('codigo_interno', '').strip()
        ca = request.POST.get('ca', '').strip()
        tamanho = request.POST.get('tamanho', '').strip()
        vida_util_meses = request.POST.get('vida_util_meses', '').strip()    
        quantidade = request.POST.get('quantidade', '').strip()

        if not nome:
            messages.error(request, "O campo Nome é obrigatório.")
        else:
            epi.nome = nome
            epi.codigo_interno = codigo_interno or None
            epi.ca = ca or None
            epi.tamanho = tamanho or None
            epi.vida_util_meses = int(vida_util_meses) if vida_util_meses else None
            epi.quantidade = int(quantidade) if quantidade else 0
            epi.save()
            messages.success(request, "EPI atualizado com sucesso!")
            return redirect("app_epi:listar_epi") 

    return render(request, "app_epi/pages/update.html", {'epi': epi})

def pagina_editar_epi(request):
    epis = Epi.objects.all()
    return render(request, 'app_epi/pages/pagina_editar_epi.html', {'epis': epis})

def delete(request, id):
    epi = get_object_or_404(Epi, pk=id)
    if request.method == "POST":
     epi.delete()
     messages.success(request, f"Epi {epi.nome} excluído com sucesso!")
     return redirect("app_epi:pagina_editar_epi")
    else:
     return render(request, "app_epi/pages/pagina_editar_epi.html", {"epi": epi})