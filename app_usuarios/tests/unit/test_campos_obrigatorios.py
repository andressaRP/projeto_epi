import pytest
from app_usuarios import views

def campos_obrigatorios_ok(nome, cpf, matricula):
    return all([nome.strip(), cpf.strip(), matricula.strip()])

def test_campos_obrigatorios_ok():
    assert not campos_obrigatorios_ok("", "1", "2")
    assert campos_obrigatorios_ok("Ana", "111", "A1")

