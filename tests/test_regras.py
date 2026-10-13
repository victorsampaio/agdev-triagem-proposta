import json

import pytest

from triagem import RECUSADA, REVISAO_HUMANA, SEGUE, avaliar
from triagem.regras import CAMPOS_OBRIGATORIOS


def motivos(resultado):
    return [(m.regra, m.resultado) for m in resultado.motivos]


# R1 - área de pastagem degradada de pelo menos 100 ha


@pytest.mark.parametrize("area, parecer", [
    pytest.param(100, SEGUE, id="exatamente-100-ha-passa"),
    pytest.param(100.01, SEGUE, id="pouco-acima-do-minimo"),
    pytest.param(99.99, RECUSADA, id="pouco-abaixo-do-minimo"),
    pytest.param(0, RECUSADA, id="area-zero"),
])
def test_r1_area_minima(proposta, area, parecer):
    assert avaliar(proposta(area_degradada_ha=area)).parecer == parecer


def test_r1_mensagem_informa_a_area_e_o_minimo(proposta):
    resultado = avaliar(proposta(area_degradada_ha=99.99))

    assert motivos(resultado) == [("R1", RECUSADA)]
    assert "99,99 ha" in resultado.motivos[0].mensagem
    assert "100 ha" in resultado.motivos[0].mensagem


@pytest.mark.parametrize("valor", [
    pytest.param(-10, id="negativo"),
    pytest.param("850", id="numero-em-texto"),
    pytest.param(True, id="booleano"),
    pytest.param([850], id="lista"),
    pytest.param(float("nan"), id="nan"),
])
def test_r1_valor_invalido_vai_para_revisao(proposta, valor):
    resultado = avaliar(proposta(area_degradada_ha=valor))

    assert resultado.parecer == REVISAO_HUMANA
    assert motivos(resultado) == [("R1", REVISAO_HUMANA)]
    assert "area_degradada_ha" in resultado.motivos[0].mensagem


# R2 - nenhum alerta de desmatamento depois de 01/01/2020 (corte confirmado pela AgDev)


@pytest.mark.parametrize("alerta, parecer", [
    pytest.param(None, SEGUE, id="sem-alerta"),
    pytest.param("2019-12-31", SEGUE, id="vespera-do-corte"),
    pytest.param("2020-01-01", SEGUE, id="dia-do-corte-nao-recusa"),
    pytest.param("01/01/2020", SEGUE, id="dia-do-corte-formato-brasileiro"),
    pytest.param("2020-01-02", RECUSADA, id="dia-seguinte-ao-corte"),
    pytest.param("2020-06-15", RECUSADA, id="alerta-em-2020-recusa-pelo-novo-corte"),
    pytest.param("15/06/2020", RECUSADA, id="formato-brasileiro"),
    pytest.param([], SEGUE, id="lista-vazia"),
    pytest.param(["2018-03-01", "2019-05-10"], SEGUE, id="lista-so-com-alertas-antigos"),
    pytest.param(["2019-05-10", "2022-08-01"], RECUSADA, id="lista-com-alerta-antigo-e-recente"),
])
def test_r2_data_de_corte(proposta, alerta, parecer):
    assert avaliar(proposta(alerta_desmatamento=alerta)).parecer == parecer


def test_r2_mensagem_cita_so_os_alertas_posteriores_ao_corte_em_ordem(proposta):
    resultado = avaliar(proposta(alerta_desmatamento=["2022-08-01", "2019-05-10", "2021-03-02"]))
    mensagem = resultado.motivos[0].mensagem

    assert motivos(resultado) == [("R2", RECUSADA)]
    assert "02/03/2021, 01/08/2022" in mensagem
    assert "10/05/2019" not in mensagem
    assert "01/01/2020" in mensagem


@pytest.mark.parametrize("alerta", [
    pytest.param("31/02/2023", id="data-impossivel"),
    pytest.param("ontem", id="texto"),
    pytest.param("", id="texto-vazio"),
    pytest.param(2023, id="numero"),
    pytest.param({"data": "2023-03-15"}, id="objeto"),
])
def test_r2_data_invalida_vai_para_revisao(proposta, alerta):
    resultado = avaliar(proposta(alerta_desmatamento=alerta))

    assert resultado.parecer == REVISAO_HUMANA
    assert motivos(resultado) == [("R2", REVISAO_HUMANA)]


def test_r2_alerta_recente_e_data_invalida_geram_os_dois_motivos(proposta):
    resultado = avaliar(proposta(alerta_desmatamento=["2022-08-01", "ontem"]))

    assert resultado.parecer == RECUSADA
    assert motivos(resultado) == [("R2", RECUSADA), ("R2", REVISAO_HUMANA)]


# R3 - situação do CAR


@pytest.mark.parametrize("situacao, parecer", [
    pytest.param("Ativo", SEGUE, id="ativo"),
    pytest.param("ativo", SEGUE, id="ativo-minusculo"),
    pytest.param(" ATIVO ", SEGUE, id="ativo-maiusculo-com-espacos"),
    pytest.param("Pendente", REVISAO_HUMANA, id="pendente"),
    pytest.param("pendente ", REVISAO_HUMANA, id="pendente-minusculo-com-espaco"),
    pytest.param("Cancelado", RECUSADA, id="cancelado"),
    pytest.param("Suspenso", RECUSADA, id="suspenso"),
    pytest.param("SUSPENSO", RECUSADA, id="suspenso-maiusculo"),
])
def test_r3_situacoes_conhecidas(proposta, situacao, parecer):
    resultado = avaliar(proposta(situacao_car=situacao))

    assert resultado.parecer == parecer
    if parecer != SEGUE:
        assert motivos(resultado) == [("R3", parecer)]


@pytest.mark.parametrize("situacao", [
    pytest.param("Em análise", id="valor-fora-da-lista"),
    pytest.param("", id="texto-vazio"),
    pytest.param(1, id="numero"),
])
def test_r3_valor_fora_da_lista_vai_para_revisao_citando_o_valor(proposta, situacao):
    resultado = avaliar(proposta(situacao_car=situacao))

    assert motivos(resultado) == [("R3", REVISAO_HUMANA)]
    assert json.dumps(situacao, ensure_ascii=False) in resultado.motivos[0].mensagem


# R4 - situação cadastral do CPF ou CNPJ


@pytest.mark.parametrize("situacao, parecer", [
    pytest.param("Regular", SEGUE, id="regular"),
    pytest.param("REGULAR", SEGUE, id="regular-maiusculo"),
    pytest.param(" regular ", SEGUE, id="regular-com-espacos"),
    pytest.param("Pendente de regularização", REVISAO_HUMANA, id="pendente-de-regularizacao"),
    pytest.param("Suspensa", REVISAO_HUMANA, id="suspensa"),
    pytest.param("", REVISAO_HUMANA, id="texto-vazio"),
])
def test_r4_situacao_cadastral(proposta, situacao, parecer):
    resultado = avaliar(proposta(situacao_cadastral=situacao))

    assert resultado.parecer == parecer
    if parecer != SEGUE:
        assert motivos(resultado) == [("R4", REVISAO_HUMANA)]


def test_r4_cnpj_ativa_segue_o_enunciado_e_vai_para_revisao(proposta):
    resultado = avaliar(proposta(situacao_cadastral="Ativa"))

    assert motivos(resultado) == [("R4", REVISAO_HUMANA)]
    assert "\"Ativa\"" in resultado.motivos[0].mensagem


# R5 - diferença entre área da matrícula e área do CAR maior que 5% da matrícula


@pytest.mark.parametrize("matricula, car, parecer", [
    pytest.param(1000, 1000, SEGUE, id="areas-iguais"),
    pytest.param(1000, 1050, SEGUE, id="exatamente-5-porcento-acima"),
    pytest.param(1000, 950, SEGUE, id="exatamente-5-porcento-abaixo"),
    pytest.param(100.1, 105.105, SEGUE, id="exatamente-5-porcento-com-decimais"),
    pytest.param(1000, 1050.1, REVISAO_HUMANA, id="5-01-porcento-acima"),
    pytest.param(1000, 949.9, REVISAO_HUMANA, id="5-01-porcento-abaixo"),
    pytest.param(1000, 1052, REVISAO_HUMANA, id="percentual-sobre-a-matricula-e-nao-sobre-o-car"),
])
def test_r5_limite_de_5_porcento(proposta, matricula, car, parecer):
    resultado = avaliar(proposta(area_matricula_ha=matricula, area_car_ha=car))

    assert resultado.parecer == parecer
    if parecer != SEGUE:
        assert motivos(resultado) == [("R5", REVISAO_HUMANA)]


def test_r5_mensagem_informa_areas_e_percentual(proposta):
    resultado = avaliar(proposta(area_matricula_ha=900, area_car_ha=1000))
    mensagem = resultado.motivos[0].mensagem

    assert "900 ha" in mensagem
    assert "1.000 ha" in mensagem
    assert "11,11%" in mensagem


@pytest.mark.parametrize("campo, valor", [
    pytest.param("area_matricula_ha", 0, id="matricula-zero"),
    pytest.param("area_matricula_ha", -5, id="matricula-negativa"),
    pytest.param("area_car_ha", -5, id="car-negativo"),
    pytest.param("area_car_ha", "1190", id="car-em-texto"),
])
def test_r5_valor_invalido_vai_para_revisao(proposta, campo, valor):
    resultado = avaliar(proposta(**{campo: valor}))

    assert motivos(resultado) == [("R5", REVISAO_HUMANA)]
    assert campo in resultado.motivos[0].mensagem


@pytest.mark.parametrize("campo", ["area_matricula_ha", "area_car_ha"])
def test_r5_sem_uma_das_areas_nao_gera_motivo_so_pendencia(proposta, campo):
    resultado = avaliar(proposta(sem=[campo]))

    assert motivos(resultado) == [("R6", REVISAO_HUMANA)]
    assert any(p.startswith("Comparar as áreas") and campo in p for p in resultado.pendencias)


# R6 - campo obrigatório ausente


@pytest.mark.parametrize("campo", list(CAMPOS_OBRIGATORIOS))
def test_r6_cada_campo_obrigatorio_ausente_vai_para_revisao(proposta, campo):
    resultado = avaliar(proposta(sem=[campo]))
    motivos_r6 = [m for m in resultado.motivos if m.regra == "R6"]

    assert resultado.parecer == REVISAO_HUMANA
    assert len(motivos_r6) == 1
    assert campo in motivos_r6[0].mensagem
    assert any(p.startswith("Obter o dado que falta") and campo in p for p in resultado.pendencias)


@pytest.mark.parametrize("campo", [c for c in CAMPOS_OBRIGATORIOS if c != "alerta_desmatamento"])
def test_r6_nulo_conta_como_ausente(proposta, campo):
    resultado = avaliar(proposta(**{campo: None}))

    assert ("R6", REVISAO_HUMANA) in motivos(resultado)
    assert any(campo in m.mensagem for m in resultado.motivos if m.regra == "R6")


def test_r6_alerta_nulo_significa_sem_alerta_e_nao_campo_ausente(proposta):
    resultado = avaliar(proposta(alerta_desmatamento=None))

    assert resultado.parecer == SEGUE
    assert resultado.motivos == ()


def test_r6_dois_campos_ausentes_aparecem_ambos(proposta):
    resultado = avaliar(proposta(sem=["id", "situacao_car"]))
    mensagens = [m.mensagem for m in resultado.motivos]

    assert motivos(resultado) == [("R6", REVISAO_HUMANA), ("R6", REVISAO_HUMANA)]
    assert "(id)" in mensagens[0]
    assert "(situacao_car)" in mensagens[1]


def test_r6_proposta_vazia_lista_os_sete_campos():
    resultado = avaliar({})

    assert resultado.parecer == REVISAO_HUMANA
    assert motivos(resultado) == [("R6", REVISAO_HUMANA)] * len(CAMPOS_OBRIGATORIOS)
