import json
from pathlib import Path

import pytest

from triagem import RECUSADA, REVISAO_HUMANA, SEGUE, avaliar

PASTA_EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"
EXEMPLOS = sorted(PASTA_EXEMPLOS.glob("P-*.json"))

ESPERADOS = {
    "P-001": (SEGUE, []),
    "P-002": (RECUSADA, ["R1"]),
    "P-003": (REVISAO_HUMANA, ["R5"]),
    "P-004": (RECUSADA, ["R2", "R3"]),
    "P-005": (REVISAO_HUMANA, ["R4", "R6"]),
}


def carregar(id_proposta):
    return json.loads((PASTA_EXEMPLOS / f"{id_proposta}.json").read_text(encoding="utf-8"))


def test_existem_os_cinco_exemplos_do_enunciado():
    assert [arquivo.stem for arquivo in EXEMPLOS] == list(ESPERADOS)


@pytest.mark.parametrize("arquivo", EXEMPLOS, ids=lambda arquivo: arquivo.stem)
def test_exemplo_e_json_valido_em_utf8(arquivo):
    proposta = json.loads(arquivo.read_text(encoding="utf-8"))
    assert proposta["id"] == arquivo.stem


@pytest.mark.parametrize("id_proposta", ESPERADOS)
def test_parecer_e_motivos_dos_exemplos(id_proposta):
    parecer_esperado, regras_esperadas = ESPERADOS[id_proposta]

    resultado = avaliar(carregar(id_proposta))

    assert resultado.id_proposta == id_proposta
    assert resultado.parecer == parecer_esperado
    assert [m.regra for m in resultado.motivos] == regras_esperadas


def test_p001_segue_sem_pendencias():
    assert avaliar(carregar("P-001")).pendencias == ()


def test_p004_recusada_lista_tambem_o_motivo_de_revisao():
    resultado = avaliar(carregar("P-004"))

    assert [(m.regra, m.resultado) for m in resultado.motivos] == [
        ("R2", RECUSADA),
        ("R3", REVISAO_HUMANA),
    ]
    assert "15/03/2023" in resultado.motivos[0].mensagem


def test_p005_aponta_o_campo_que_falta_e_a_comparacao_de_areas_pendente():
    resultado = avaliar(carregar("P-005"))

    assert "area_matricula_ha" in resultado.motivos[-1].mensagem
    assert any("Comparar as áreas" in p for p in resultado.pendencias)
    assert any("area_matricula_ha" in p for p in resultado.pendencias)
