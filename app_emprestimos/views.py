from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Emprestimo
from app_usuarios.models import Colaborador
from app_epi.models import Epi

# --- LISTA com busca e filtro ---
def listar(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    qs = Emprestimo.objects.select_related("colaborador", "epi").order_by("-data_emprestimo")

    if q:
        qs = qs.filter(
            Q(colaborador__nome__icontains=q) |
            Q(colaborador__matricula__icontains=q) |
            Q(epi__nome__icontains=q) |
            Q(epi__codigo_interno__icontains=q)
        )

    if status:
        qs = qs.filter(status=status)

    # opções para o select
    status_choices = Emprestimo.Status.choices

    return render(request, "emprestimos/pages/listar.html", {
        "itens": qs,
        "q": q,
        "status_sel": status,
        "status_choices": status_choices
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

    
        if not (colaborador_id and epi_id and status):
            colaboradores = Colaborador.objects.order_by("nome")
            epis = Epi.objects.order_by("nome")
            return render(request, "emprestimos/pages/cadastrar.html", {
                "colaboradores": colaboradores,
                "epis": epis,
            })

        # regra: para “emprestado/em_uso”, recomenda ter prevista futura
        if status in [Emprestimo.Status.EMPRESTADO, Emprestimo.Status.EM_USO] and data_prevista:
            base = data_emprestimo or timezone.now()
            if data_prevista <= base:
                colaboradores = Colaborador.objects.order_by("nome")
                epis = Epi.objects.order_by("nome")
                return render(request, "emprestimos/pages/cadastrar.html", {
                    "colaboradores": colaboradores,
                    "epis": epis,
                })

        Emprestimo.objects.create(
            colaborador_id=colaborador_id,
            epi_id=epi_id,
            status=status,
            data_emprestimo=data_emprestimo or timezone.now(),
            data_prevista_devolucao=data_prevista,
        )
        return redirect("app_emprestimos:listar")

    # GET → carrega selects
    colaboradores = Colaborador.objects.order_by("nome")
    epis = Epi.objects.order_by("nome")
    return render(request, "emprestimos/pages/cadastrar.html", {
        "colaboradores": colaboradores,
        "epis": epis,
    })

# --- EDITAR (libera todos os status) ---
def editar(request, pk):
    obj = get_object_or_404(Emprestimo, pk=pk)

    if request.method == "POST":
        has_error = False

        colaborador_id = request.POST.get("colaborador") or obj.colaborador_id
        epi_id         = request.POST.get("epi") or obj.epi_id
        status         = request.POST.get("status") or obj.status

        d_emp  = _parse_dt(request.POST.get("data_emprestimo"))
        d_prev = _parse_dt(request.POST.get("data_prevista_devolucao"))
        d_dev  = _parse_dt(request.POST.get("data_devolucao"))
        obs    = (request.POST.get("observacao_devolucao") or "").strip()

        base_emp = d_emp or obj.data_emprestimo or timezone.now()

        # validações
        if d_prev and d_prev <= base_emp:
            messages.error(request, "A data prevista de devolução deve ser posterior à data do empréstimo.")
            has_error = True

        finais = {Emprestimo.Status.DEVOLVIDO, Emprestimo.Status.DANIFICADO, Emprestimo.Status.PERDIDO}
        if d_dev and d_dev < base_emp:
            messages.error(request, "A data da devolução não pode ser anterior à data do empréstimo.")
            has_error = True
        if status in finais and not d_dev:
            messages.error(request, "Para status final (Devolvido/Danificado/Perdido), informe a data da devolução.")
            has_error = True

        if has_error:
            # >>> PRÉ-PREENCHER O OBJETO COM O QUE O USUÁRIO DIGITOU (NÃO SALVAR)
            obj.colaborador_id = colaborador_id
            obj.epi_id         = epi_id
            obj.status         = status
            if d_emp:
                obj.data_emprestimo = d_emp
            obj.data_prevista_devolucao = d_prev
            obj.data_devolucao          = d_dev
            obj.observacao_devolucao    = obs or None

            colaboradores = Colaborador.objects.order_by("nome")
            epis = Epi.objects.order_by("nome")
            return render(request, "emprestimos/pages/cadastrar.html", {
                "modo": "editar",
                "obj": obj, 
                "colaboradores": colaboradores,
                "epis": epis,
                "status_choices": [(s.value, s.label) for s in Emprestimo.Status],
                "is_final": status in {"devolvido","danificado","perdido"},
            })

        # sem erros -> salvar
        obj.colaborador_id = colaborador_id
        obj.epi_id         = epi_id
        obj.status         = status
        if d_emp:
            obj.data_emprestimo = d_emp
        obj.data_prevista_devolucao = d_prev
        if status in finais:
            obj.data_devolucao = d_dev
            obj.observacao_devolucao = obs or None
        else:
            obj.data_devolucao = None
            obj.observacao_devolucao = None

        obj.save()
        messages.success(request, "Empréstimo atualizado com sucesso.")
        return redirect("app_emprestimos:listar")

    # GET
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

# --- PAINEL por colaborador (quantos EPIs cada um tem em aberto) ---
def painel_colaboradores(request):
    # Em "aberto" considero: emprestado/em_uso/fornecido (não finais)
    abertos = Emprestimo.objects.filter(status__in=["emprestado","em_uso","fornecido"])
    resumo = (abertos
              .values("colaborador__id","colaborador__nome","colaborador__matricula")
              .annotate(qtd=Count("id"))
              .order_by("colaborador__nome"))
    return render(request, "emprestimos/pages/painel_colaboradores.html", {"resumo": resumo})
