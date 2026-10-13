import pytest

PROPOSTA_BASE = {
    "id": "P-TESTE",
    "area_degradada_ha": 850,
    "area_matricula_ha": 1200,
    "area_car_ha": 1190,
    "alerta_desmatamento": None,
    "situacao_car": "Ativo",
    "situacao_cadastral": "Regular",
}


@pytest.fixture
def proposta():
    """Monta a proposta-base (parecer SEGUE) com campos alterados ou removidos."""

    def montar(sem=(), **mudancas):
        resultado = {campo: valor for campo, valor in PROPOSTA_BASE.items() if campo not in sem}
        resultado.update(mudancas)
        return resultado

    return montar
