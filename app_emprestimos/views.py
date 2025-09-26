from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Emprestimo
from app_usuarios.models import Colaborador
from app_epi.models import Epi

# --- LISTA com busca e filtro ---
def _por_status():
    label = dict(Emprestimo.Status.choices)
    qs = (Emprestimo.objects
          .values('status')
          .annotate(qtd=Count('id'))
          .order_by('status'))
    return [{"status": label.get(r["status"], r["status"]).title(), "qtd": r["qtd"]} for r in qs]

def listar(request):
    # filtros vindos do template
    q = (request.GET.get("q") or "").strip()
    status_sel = (request.GET.get("status") or "").strip()
    colaborador_nome = (request.GET.get("colaborador_nome") or "").strip()
    equipamento_nome = (request.GET.get("equipamento_nome") or "").strip()

    qs = Emprestimo.objects.select_related("colaborador", "epi").order_by("-data_emprestimo")

    # filtro unificado (campo "q")
    if q:
        qs = qs.filter(
            Q(colaborador__nome__icontains=q) |
            Q(colaborador__matricula__icontains=q) |
            Q(epi__nome__icontains=q) |
            Q(epi__codigo_interno__icontains=q)
        )

    # filtros separados (se vierem do template com campos específicos)
    if colaborador_nome:
        qs = qs.filter(colaborador__nome__icontains=colaborador_nome)
    if equipamento_nome:
        qs = qs.filter(epi__nome__icontains=equipamento_nome)

    # filtro por status
    if status_sel:
        qs = qs.filter(status=status_sel)

    # opções para o select
    status_choices = Emprestimo.Status.choices

    # métricas úteis
    total = qs.count()
    abertos = qs.filter(status=Emprestimo.Status.EMPRESTADO, data_devolucao__isnull=True).count()

    return render(request, "emprestimos/pages/listar.html", {
        "itens": qs,
        # estados dos filtros (p/ manter preenchido no form)
        "q": q,
        "status_sel": status_sel,
        "colaborador_nome": colaborador_nome,
        "equipamento_nome": equipamento_nome,
        "status_choices": status_choices,

        # badges no topo do relatório
        "por_status": _por_status(),

        # métricas 
        "total": total,
        "abertos": abertos,

        # controlar botões Excluir em finalizados
        "FINALIZADOS": [s.value for s in FINALIZADOS],
    })

def _parse_dt(s):
    if not s: return None
    try:
        dt = timezone.datetime.fromisoformat(s)  # 'YYYY-MM-DDTHH:MM'
    except ValueError:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def cadastrar(request):
    if request.method == "POST":
        colaborador_id = request.POST.get("colaborador")
        epi_id = request.POST.get("epi")
        status = request.POST.get("status")
        data_emprestimo = _parse_dt(request.POST.get("data_emprestimo"))
        data_prevista = _parse_dt(request.POST.get("data_prevista_devolucao"))
        condicao_txt = (request.POST.get("condicao_emprestimo") or "").strip()

        # validação básica
        if not (colaborador_id and epi_id and status):
            messages.error(request, "Colaborador, EPI e Status são obrigatórios.")
            colaboradores = Colaborador.objects.order_by("nome")
            epis = Epi.objects.order_by("nome")
            return render(request, "emprestimos/pages/cadastrar.html", {
                "colaboradores": colaboradores,
                "epis": epis,
            })

        base = data_emprestimo or timezone.now()

        # para emprestado → precisa de data prevista futura
        if status == Emprestimo.Status.EMPRESTADO:
            if not data_prevista:
                messages.error(request, "Informe a data prevista de devolução para empréstimos.")
                colaboradores = Colaborador.objects.order_by("nome")
                epis = Epi.objects.order_by("nome")
                return render(request, "emprestimos/pages/cadastrar.html", {
                    "colaboradores": colaboradores,
                    "epis": epis,
                })
            if data_prevista <= base:
                messages.error(request, "A data prevista deve ser posterior à data do empréstimo.")
                colaboradores = Colaborador.objects.order_by("nome")
                epis = Epi.objects.order_by("nome")
                return render(request, "emprestimos/pages/cadastrar.html", {
                    "colaboradores": colaboradores,
                    "epis": epis,
                })

        # para fornecido → ignora data_prevista
        if status == Emprestimo.Status.FORNECIDO:
            data_prevista = None

        # salvar
        Emprestimo.objects.create(
            colaborador_id=colaborador_id,
            epi_id=epi_id,
            status=status,
            data_emprestimo=data_emprestimo or timezone.now(),
            data_prevista_devolucao=data_prevista,
            condicao_emprestimo=condicao_txt or None,
        )
        messages.success(request, "Empréstimo cadastrado com sucesso!")
        return redirect("app_emprestimos:listar")

    # GET → carrega selects
    colaboradores = Colaborador.objects.order_by("nome")
    epis = Epi.objects.order_by("nome")
    return render(request, "emprestimos/pages/cadastrar.html", {
        "colaboradores": colaboradores,
        "epis": epis,
    })


# --- EDITAR (libera todos os status) ---
def _to_int_or_none(v):
    try:
        return int(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None

FINAIS = {
    Emprestimo.Status.DEVOLVIDO,
    Emprestimo.Status.DANIFICADO,
    Emprestimo.Status.PERDIDO,
}

def editar(request, pk):
    obj = get_object_or_404(Emprestimo, pk=pk)

    if request.method == "POST":
        # Só lemos o que pode mudar
        status = request.POST.get("status") or obj.status
        d_dev  = _parse_dt(request.POST.get("data_devolucao"))

        has_error = False
        base_emp  = obj.data_emprestimo or timezone.now()

        # validação: se finaliza, precisa da data; e não pode ser antes do empréstimo
        if status in FINAIS and not d_dev:
            messages.error(request, "Para status final (Devolvido/Danificado/Perdido), informe a data da devolução.")
            has_error = True
        if d_dev and d_dev < base_emp:
            messages.error(request, "A data da devolução não pode ser anterior à data do empréstimo.")
            has_error = True

        if has_error:
            colaboradores = Colaborador.objects.order_by("nome")
            epis = Epi.objects.order_by("nome")
            return render(request, "emprestimos/pages/cadastrar.html", {
                "modo": "editar",
                "obj": obj,  # mostramos os dados atuais
                "colaboradores": colaboradores,
                "epis": epis,
                "status_choices": [(s.value, s.label) for s in Emprestimo.Status],
                "is_final": status in {"devolvido","danificado","perdido"},
            })

        #  aplica SOMENTE status e data_devolucao
        obj.status = status
        if status in FINAIS:
            obj.data_devolucao = d_dev
        else:
            obj.data_devolucao = None
            obj.observacao_devolucao = None  # limpar observação

        obj.save(update_fields=["status", "data_devolucao"])
        messages.success(request, "Empréstimo atualizado com sucesso.")
        return redirect("app_emprestimos:relatorio")  # volta ao relatório

    # GET → renderiza tela de edição com campos travados (no template)
    colaboradores = Colaborador.objects.order_by("nome")
    epis = Epi.objects.order_by("nome")
    return render(request, "emprestimos/pages/cadastrar.html", {
        "modo": "editar",
        "obj": obj,
        "colaboradores": colaboradores,
        "epis": epis,
        "status_choices": [(s.value, s.label) for s in Emprestimo.Status],
        "is_final": obj.status in {"devolvido","danificado","perdido"},
    })

# --- APAGAR (só se finalizado) ---
FINALIZADOS = {
    Emprestimo.Status.DEVOLVIDO,
    Emprestimo.Status.DANIFICADO,  
    Emprestimo.Status.PERDIDO,     
}

def apagar(request, pk):
    emp = get_object_or_404(Emprestimo, pk=pk)

    # só pode apagar se estiver finalizado
    if emp.status not in FINALIZADOS:
        messages.error(request, "Só é possível excluir empréstimos finalizados (ex.: Devolvido).")
        return redirect('app_emprestimos:listar')

    if request.method == "POST":
        emp.delete()
        messages.success(request, "Empréstimo excluído com sucesso.")
        return redirect('app_emprestimos:listar')

    # GET → confirma antes de excluir
    return render(request, "emprestimos/pages/confirmar_delete.html", {"emp": emp})



def relatorio(request):
    qs = (Emprestimo.objects
          .select_related("colaborador","epi")
          .order_by("-data_emprestimo"))

    # filtros AND
    colab_nome = (request.GET.get("colaborador_nome") or "").strip()
    epi_nome   = (request.GET.get("equipamento_nome") or "").strip()
    status     = (request.GET.get("status") or "").strip()

    if colab_nome:
        qs = qs.filter(colaborador__nome__icontains=colab_nome)
    if epi_nome:
        qs = qs.filter(epi__nome__icontains=epi_nome)
    if status:
        qs = qs.filter(status=status)

    total = qs.count()
    abertos = qs.exclude(status__in=["devolvido","danificado","perdido"]).count()
    por_status = qs.values("status").annotate(qtd=Count("id")).order_by()

    context = {
        "itens": qs,
        "status_choices": Emprestimo.Status.choices,
        "status_sel": status,
        "colaborador_nome": colab_nome,
        "equipamento_nome": epi_nome,
        "total": total,
        "abertos": abertos,
        "por_status": por_status,
    }
    return render(request, "emprestimos/pages/relatorio.html", context)