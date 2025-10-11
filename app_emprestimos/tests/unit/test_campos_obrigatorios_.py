from django.urls import reverse, resolve
from app_emprestimos import views

def campos_obrigatorios_ok(colaborador, epi, data_emprestimo):
    """Retorna True se todos os campos obrigatórios do empréstimo foram preenchidos."""
    return all([str(colaborador).strip(), str(epi).strip(), str(data_emprestimo).strip()])


def test_campos_obrigatorios_ok():
    """Verifica se o empréstimo tem todos os campos obrigatórios preenchidos."""

    # Caso 1: colaborador ausente → deve falhar (False)
    assert not campos_obrigatorios_ok("", "Capacete", "2025-10-10"), "Colaborador vazio não deve ser aceito"

    # Caso 2: EPI ausente → deve falhar (False)
    assert not campos_obrigatorios_ok("João", "", "2025-10-10"), "EPI vazio não deve ser aceito"

    # Caso 3: Data ausente → deve falhar (False)
    assert not campos_obrigatorios_ok("João", "Capacete", ""), "Data vazia não deve ser aceita"

    # Caso 4: Todos preenchidos → deve passar (True)
    assert campos_obrigatorios_ok("João", "Capacete", "2025-10-10"), "Campos válidos devem ser aceitos"