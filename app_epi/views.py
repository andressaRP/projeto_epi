from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError
from django.utils import timezone
from django.db.models import Q, Count, F
from django.db.models.functions import Coalesce
from .models import Epi
from app_emprestimos.models import Emprestimo
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
        elif Epi.objects.filter(codigo_interno=codigo_interno).exists():
            messages.error(request, "Já existe um EPI com este código interno.")
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

def delete(request, id):
    epi = get_object_or_404(Epi, pk=id)

    if request.method == "POST":
        try:
            epi.delete()
            messages.success(request, f"EPI {epi.nome} excluído com sucesso!")
        except ProtectedError:
            messages.error(request, "Não é possível excluir: existem empréstimos vinculados.")
        return redirect("app_epi:listar_epi")

    # GET → mostra tela de confirmação
    return render(request, "app_epi/pages/confirmar_delete.html", {"epi": epi})

def relatorio_epi(request):
    hoje = timezone.now().date()

    epis = (
        Epi.objects
        .annotate(
            # total de movimentações (empréstimos) por EPI
            total=Count('emprestimos', distinct=True),

            # abertos que contam como uso: apenas EMPRESTADO (FORNECIDO não entra como atrasado)
            emprestados=Count(
                'emprestimos',
                filter=Q(emprestimos__status=Emprestimo.Status.EMPRESTADO),
                distinct=True
            ),

            # somente EMPRESTADO vencido conta como atrasado
            atrasados=Count(
                'emprestimos',
                filter=Q(emprestimos__status=Emprestimo.Status.EMPRESTADO) &
                        Q(emprestimos__data_prevista_devolucao__isnull=False) &
                        Q(emprestimos__data_prevista_devolucao__lt=hoje),
                distinct=True
            ),

            # demais status (não entram no atraso)
            fornecidos=Count(
                'emprestimos',
                filter=Q(emprestimos__status=Emprestimo.Status.FORNECIDO),
                distinct=True
            ),
            devolvidos=Count(
                'emprestimos',
                filter=Q(emprestimos__status=Emprestimo.Status.DEVOLVIDO),
                distinct=True
            ),
            danificados=Count(
                'emprestimos',
                filter=Q(emprestimos__status=Emprestimo.Status.DANIFICADO),
                distinct=True
            ),
            perdidos=Count(
                'emprestimos',
                filter=Q(emprestimos__status=Emprestimo.Status.PERDIDO),
                distinct=True
            ),
        )
        .annotate(
            # em uso = emprestados + fornecidos
            em_uso=F('emprestados') + F('fornecidos'),
            # disponível = quantidade - em uso  
            disponivel=Coalesce(F('quantidade'), 0)
                       - (Coalesce(F('emprestados'), 0) + Coalesce(F('fornecidos'), 0)),
        )
        .order_by('nome')
    )

    # Mantém o formato esperado no template
    dados = [{
        "epi": e,
        "total": e.total,
        "emprestados": e.emprestados,
        "fornecidos": e.fornecidos,
        "devolvidos": e.devolvidos,
        "danificados": e.danificados,
        "perdidos": e.perdidos,
        "atrasados": e.atrasados,       #  só EMPRESTADO vencido
        "em_uso": e.em_uso,
        "disponivel": max(e.disponivel, 0),  # evita número negativo
    } for e in epis]

    return render(request, "app_epi/pages/relatorio.html", {"dados": dados})