"""Regras de triagem R1 a R6.

Os parâmetros de negócio ficam no topo do arquivo. Quando o comitê mudar uma regra,
altere o parâmetro, ajuste os testes e suba VERSAO_REGRAS.
"""

import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal

VERSAO_REGRAS = "1.0.0"

AREA_MINIMA_HA = Decimal("100")
DATA_CORTE_DESMATAMENTO = date(2020, 1, 1)
TOLERANCIA_DIFERENCA_AREA = Decimal("0.05")

CAMPOS_OBRIGATORIOS = {
    "id": "identificador da proposta",
    "area_degradada_ha": "área de pastagem degradada",
    "area_matricula_ha": "área da matrícula",
    "area_car_ha": "área do CAR",
    "alerta_desmatamento": "alerta de desmatamento",
    "situacao_car": "situação do CAR",
    "situacao_cadastral": "situação cadastral do CPF/CNPJ",
}
CAMPOS_QUE_ACEITAM_NULO = {"alerta_desmatamento"}

SEGUE = "SEGUE"
RECUSADA = "RECUSADA"
REVISAO_HUMANA = "REVISÃO HUMANA"

SITUACOES_CAR = {
    "ativo": SEGUE,
    "pendente": REVISAO_HUMANA,
    "cancelado": RECUSADA,
    "suspenso": RECUSADA,
}
SITUACAO_CADASTRAL_ACEITA = "regular"

FORMATOS_DATA = ("%Y-%m-%d", "%d/%m/%Y")


@dataclass(frozen=True)
class Achado:
    """Resultado de uma regra que não passou.

    `resultado` é None quando a regra não pôde ser avaliada: nesse caso o achado
    gera só uma pendência, e o motivo do parecer vem de outra regra.
    """

    regra: str
    resultado: str | None
    mensagem: str
    pendencia: str


def _ausente(proposta, campo):
    if campo not in proposta:
        return True
    return proposta[campo] is None and campo not in CAMPOS_QUE_ACEITAM_NULO


def _mostrar(valor):
    return json.dumps(valor, ensure_ascii=False)


def _normalizar(valor):
    return valor.strip().casefold() if isinstance(valor, str) else None


def _ler_area(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    area = Decimal(str(valor))
    if not area.is_finite() or area < 0:
        return None
    return area


def _ler_data(valor):
    if not isinstance(valor, str):
        return None
    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(valor.strip(), formato).date()
        except ValueError:
            continue
    return None


def _numero(valor):
    if valor == valor.to_integral_value():
        valor = valor.quantize(Decimal(1))
    else:
        valor = valor.normalize()
    return f"{valor:,f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _data(valor):
    return valor.strftime("%d/%m/%Y")


def _campo(campo):
    return f"{CAMPOS_OBRIGATORIOS[campo]} ({campo})"


def _valor_invalido(regra, campo, valor):
    return Achado(
        regra,
        REVISAO_HUMANA,
        f"Valor inválido em {_campo(campo)}: {_mostrar(valor)}.",
        f"Corrigir o valor de {_campo(campo)}.",
    )


def r1_area_minima(proposta):
    if _ausente(proposta, "area_degradada_ha"):
        return []
    valor = proposta["area_degradada_ha"]
    area = _ler_area(valor)
    if area is None:
        return [_valor_invalido("R1", "area_degradada_ha", valor)]
    if area < AREA_MINIMA_HA:
        return [Achado(
            "R1",
            RECUSADA,
            f"Área de pastagem degradada de {_numero(area)} ha, abaixo do mínimo de "
            f"{_numero(AREA_MINIMA_HA)} ha.",
            f"Comunicar ao proponente a recusa: área degradada abaixo de {_numero(AREA_MINIMA_HA)} ha.",
        )]
    return []


def r2_desmatamento(proposta):
    if _ausente(proposta, "alerta_desmatamento"):
        return []
    valor = proposta["alerta_desmatamento"]
    if valor is None:
        return []
    alertas = valor if isinstance(valor, list) else [valor]

    datas, invalidos = [], []
    for alerta in alertas:
        data = _ler_data(alerta)
        if data is None:
            invalidos.append(alerta)
        else:
            datas.append(data)

    achados = []
    posteriores = sorted(data for data in datas if data > DATA_CORTE_DESMATAMENTO)
    if posteriores:
        achados.append(Achado(
            "R2",
            RECUSADA,
            f"Alerta de desmatamento em {', '.join(_data(d) for d in posteriores)}, "
            f"posterior a {_data(DATA_CORTE_DESMATAMENTO)}.",
            f"Comunicar ao proponente a recusa: alerta de desmatamento posterior a "
            f"{_data(DATA_CORTE_DESMATAMENTO)}.",
        ))
    if invalidos:
        achados.append(Achado(
            "R2",
            REVISAO_HUMANA,
            f"Data de alerta de desmatamento inválida: {', '.join(_mostrar(v) for v in invalidos)}.",
            "Conferir a data do alerta de desmatamento na fonte original.",
        ))
    return achados


def r3_situacao_car(proposta):
    if _ausente(proposta, "situacao_car"):
        return []
    valor = proposta["situacao_car"]
    resultado = SITUACOES_CAR.get(_normalizar(valor))
    if resultado == SEGUE:
        return []
    if resultado == RECUSADA:
        return [Achado(
            "R3",
            RECUSADA,
            f"Situação do CAR é {_mostrar(valor)}.",
            "Comunicar ao proponente a recusa: CAR cancelado ou suspenso.",
        )]
    if resultado == REVISAO_HUMANA:
        return [Achado(
            "R3",
            REVISAO_HUMANA,
            f"Situação do CAR é {_mostrar(valor)}.",
            "Verificar com o proponente a regularização do CAR.",
        )]
    return [Achado(
        "R3",
        REVISAO_HUMANA,
        f"Situação do CAR não reconhecida: {_mostrar(valor)}.",
        "Confirmar a situação do CAR no SICAR.",
    )]


def r4_situacao_cadastral(proposta):
    if _ausente(proposta, "situacao_cadastral"):
        return []
    valor = proposta["situacao_cadastral"]
    if _normalizar(valor) == SITUACAO_CADASTRAL_ACEITA:
        return []
    return [Achado(
        "R4",
        REVISAO_HUMANA,
        f"Situação cadastral do CPF/CNPJ é {_mostrar(valor)}, e não \"Regular\".",
        "Verificar a situação cadastral do CPF/CNPJ na Receita Federal.",
    )]


def r5_diferenca_areas(proposta):
    faltando = [c for c in ("area_matricula_ha", "area_car_ha") if _ausente(proposta, c)]
    if faltando:
        return [Achado(
            "R5",
            None,
            "Não foi possível comparar as áreas da matrícula e do CAR.",
            "Comparar as áreas da matrícula e do CAR depois de obter "
            f"{' e '.join(_campo(c) for c in faltando)}.",
        )]

    valor_matricula = proposta["area_matricula_ha"]
    valor_car = proposta["area_car_ha"]
    matricula = _ler_area(valor_matricula)
    car = _ler_area(valor_car)

    achados = []
    if matricula is None or matricula == 0:
        achados.append(_valor_invalido("R5", "area_matricula_ha", valor_matricula))
    if car is None:
        achados.append(_valor_invalido("R5", "area_car_ha", valor_car))
    if achados:
        return achados

    diferenca = abs(matricula - car)
    if diferenca > TOLERANCIA_DIFERENCA_AREA * matricula:
        percentual = (diferenca / matricula * 100).quantize(Decimal("0.01"), ROUND_HALF_UP)
        return [Achado(
            "R5",
            REVISAO_HUMANA,
            f"Diferença de {_numero(diferenca)} ha entre a área da matrícula "
            f"({_numero(matricula)} ha) e a área do CAR ({_numero(car)} ha): "
            f"{_numero(percentual)}% da matrícula, acima do limite de "
            f"{_numero(TOLERANCIA_DIFERENCA_AREA * 100)}%.",
            "Conferir a divergência entre a área da matrícula e a área do CAR.",
        )]
    return []


def r6_campos_obrigatorios(proposta):
    return [
        Achado(
            "R6",
            REVISAO_HUMANA,
            f"Campo obrigatório ausente: {_campo(campo)}.",
            f"Obter o dado que falta: {_campo(campo)}.",
        )
        for campo in CAMPOS_OBRIGATORIOS
        if _ausente(proposta, campo)
    ]


REGRAS = (
    r1_area_minima,
    r2_desmatamento,
    r3_situacao_car,
    r4_situacao_cadastral,
    r5_diferenca_areas,
    r6_campos_obrigatorios,
)
