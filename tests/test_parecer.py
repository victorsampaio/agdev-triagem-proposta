import copy
import json
from datetime import date

import pytest

from triagem import RECUSADA, REVISAO_HUMANA, SEGUE, VERSAO_REGRAS, avaliar, regras


def motivos(resultado):
    return [(m.regra, m.resultado) for m in resultado.motivos]


def test_recusada_prevalece_sobre_revisao_e_lista_todos_os_motivos(proposta):
    resultado = avaliar(proposta(area_degradada_ha=50, situacao_cadastral="Suspensa"))

    assert resultado.parecer == RECUSADA
    assert motivos(resultado) == [("R1", RECUSADA), ("R4", REVISAO_HUMANA)]
    assert len(resultado.pendencias) == 2


def test_duas_recusas_ao_mesmo_tempo(proposta):
    resultado = avaliar(proposta(area_degradada_ha=50, situacao_car="Cancelado"))

    assert resultado.parecer == RECUSADA
    assert motivos(resultado) == [("R1", RECUSADA), ("R3", RECUSADA)]


def test_so_motivos_de_revisao_resultam_em_revisao_humana(proposta):
    resultado = avaliar(proposta(situacao_car="Pendente", situacao_cadastral="Ativa"))

    assert resultado.parecer == REVISAO_HUMANA
    assert motivos(resultado) == [("R3", REVISAO_HUMANA), ("R4", REVISAO_HUMANA)]


def test_segue_nao_tem_motivos_nem_pendencias(proposta):
    resultado = avaliar(proposta())

    assert resultado.parecer == SEGUE
    assert resultado.motivos == ()
    assert resultado.pendencias == ()


def test_motivos_aparecem_sempre_na_ordem_das_regras(proposta):
    resultado = avaliar(proposta(
        sem=["id"],
        area_degradada_ha=50,
        alerta_desmatamento="2023-03-15",
        situacao_car="Cancelado",
        situacao_cadastral="Ativa",
        area_car_ha=2000,
    ))

    assert [m.regra for m in resultado.motivos] == ["R1", "R2", "R3", "R4", "R5", "R6"]


def test_mesma_entrada_gera_sempre_o_mesmo_resultado(proposta):
    entrada = proposta(area_degradada_ha=50, situacao_car="Pendente", sem=["id"])
    mesma_entrada_em_outra_ordem = dict(reversed(list(entrada.items())))

    primeiro = avaliar(entrada)

    assert avaliar(entrada) == primeiro
    assert avaliar(mesma_entrada_em_outra_ordem) == primeiro


def test_avaliar_nao_altera_a_proposta_recebida(proposta):
    entrada = proposta(alerta_desmatamento=["2022-08-01", "ontem"])
    copia = copy.deepcopy(entrada)

    avaliar(entrada)

    assert entrada == copia


def test_como_dict_gera_json_com_todos_os_campos(proposta):
    dados = avaliar(proposta(situacao_car="Pendente")).como_dict()
    texto = json.dumps(dados, ensure_ascii=False)

    assert list(dados) == ["id", "parecer", "versao_regras", "motivos", "pendencias"]
    assert json.loads(texto) == dados
    assert "\"REVISÃO HUMANA\"" in texto
    assert dados["versao_regras"] == VERSAO_REGRAS
    assert dados["motivos"] == [{
        "regra": "R3",
        "resultado": REVISAO_HUMANA,
        "mensagem": "Situação do CAR é \"Pendente\".",
    }]
    assert dados["pendencias"] == ["Verificar com o proponente a regularização do CAR."]


@pytest.mark.parametrize("entrada", [[], "texto", None, 42], ids=["lista", "texto", "nulo", "numero"])
def test_entrada_que_nao_e_objeto_json_gera_erro_claro(entrada):
    with pytest.raises(TypeError, match="objeto JSON"):
        avaliar(entrada)


@pytest.mark.parametrize("valor", [None, "", "   "], ids=["nulo", "vazio", "so-espacos"])
def test_proposta_sem_id_e_identificada_como_sem_id(proposta, valor):
    assert avaliar(proposta(id=valor)).id_proposta == "(sem id)"


def test_id_numerico_vira_texto(proposta):
    assert avaliar(proposta(id=123)).id_proposta == "123"


def test_mudar_uma_regra_e_mudar_um_parametro(proposta, monkeypatch):
    entrada = proposta(alerta_desmatamento="2020-06-15")
    assert avaliar(entrada).parecer == RECUSADA

    monkeypatch.setattr(regras, "DATA_CORTE_DESMATAMENTO", date(2021, 1, 1))

    assert avaliar(entrada).parecer == SEGUE
