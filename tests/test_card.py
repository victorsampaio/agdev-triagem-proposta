import json
from pathlib import Path

import pytest

from triagem import RECUSADA, REVISAO_HUMANA, SEGUE, VERSAO_REGRAS, avaliar
from triagem.card import PROXIMO_PASSO, gerar_card

PASTA_EXEMPLOS = Path(__file__).resolve().parent.parent / "exemplos"


def card_do_exemplo(id_proposta):
    proposta = json.loads((PASTA_EXEMPLOS / f"{id_proposta}.json").read_text(encoding="utf-8"))
    return gerar_card(avaliar(proposta))


def pendencias(card):
    return [linha for linha in card.splitlines() if linha.startswith("- [ ] ")]


def test_titulo_tem_o_id_e_o_parecer():
    assert card_do_exemplo("P-004").splitlines()[0] == "# Triagem P-004: RECUSADA"


def test_secoes_aparecem_na_ordem():
    card = card_do_exemplo("P-004")

    posicoes = [card.index(secao) for secao in ("**Parecer:**", "## Motivos", "## Pendências", "## Próximo passo")]

    assert posicoes == sorted(posicoes)


def test_card_mostra_a_versao_das_regras():
    assert f"**Versão das regras:** {VERSAO_REGRAS}" in card_do_exemplo("P-001")


def test_card_de_proposta_que_segue_nao_tem_motivos_nem_pendencias():
    card = card_do_exemplo("P-001")

    assert "**Parecer:** SEGUE" in card
    assert "Nenhum motivo: a proposta atende às regras R1 a R6." in card
    assert "Nenhuma pendência." in card
    assert pendencias(card) == []
    assert "Encaminhar a proposta ao comitê de crédito" in card


def test_card_recusado_lista_todos_os_motivos_e_pendencias_como_checklist():
    card = card_do_exemplo("P-004")

    assert "- **R2 (RECUSADA):** Alerta de desmatamento em 15/03/2023, posterior a 01/01/2020." in card
    assert "- **R3 (REVISÃO HUMANA):** Situação do CAR é \"Pendente\"." in card
    assert pendencias(card) == [
        "- [ ] Comunicar ao proponente a recusa: alerta de desmatamento posterior a 01/01/2020.",
        "- [ ] Verificar com o proponente a regularização do CAR.",
    ]


def test_card_de_campo_ausente_diz_qual_campo_falta_e_o_que_fazer():
    card = card_do_exemplo("P-005")

    assert "- **R6 (REVISÃO HUMANA):** Campo obrigatório ausente: área da matrícula (area_matricula_ha)." in card
    assert any(linha.startswith("- [ ] Comparar as áreas") for linha in pendencias(card))
    assert any("area_matricula_ha" in linha for linha in pendencias(card))


@pytest.mark.parametrize("id_proposta, parecer", [
    ("P-001", SEGUE),
    ("P-003", REVISAO_HUMANA),
    ("P-002", RECUSADA),
])
def test_proximo_passo_depende_do_parecer(id_proposta, parecer):
    card = card_do_exemplo(id_proposta)

    assert card.rstrip().endswith(PROXIMO_PASSO[parecer])


def test_mesma_proposta_gera_sempre_o_mesmo_card():
    assert card_do_exemplo("P-005") == card_do_exemplo("P-005")


def test_card_termina_com_quebra_de_linha():
    assert card_do_exemplo("P-001").endswith("\n")
