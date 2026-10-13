"""Consolidação das regras em um parecer: RECUSADA > REVISÃO HUMANA > SEGUE."""

from dataclasses import dataclass

from triagem.regras import RECUSADA, REGRAS, REVISAO_HUMANA, SEGUE, VERSAO_REGRAS, Achado

SEM_ID = "(sem id)"


@dataclass(frozen=True)
class Parecer:
    id_proposta: str
    parecer: str
    motivos: tuple[Achado, ...]
    pendencias: tuple[str, ...]
    versao_regras: str = VERSAO_REGRAS

    def como_dict(self):
        return {
            "id": self.id_proposta,
            "parecer": self.parecer,
            "versao_regras": self.versao_regras,
            "motivos": [
                {"regra": m.regra, "resultado": m.resultado, "mensagem": m.mensagem}
                for m in self.motivos
            ],
            "pendencias": list(self.pendencias),
        }


def avaliar(proposta):
    if not isinstance(proposta, dict):
        raise TypeError("A proposta deve ser um objeto JSON, no formato {\"campo\": valor}.")

    achados = [achado for regra in REGRAS for achado in regra(proposta)]
    motivos = tuple(a for a in achados if a.resultado is not None)
    resultados = {m.resultado for m in motivos}

    if RECUSADA in resultados:
        parecer = RECUSADA
    elif REVISAO_HUMANA in resultados:
        parecer = REVISAO_HUMANA
    else:
        parecer = SEGUE

    return Parecer(
        id_proposta=_identificar(proposta),
        parecer=parecer,
        motivos=motivos,
        pendencias=tuple(dict.fromkeys(a.pendencia for a in achados)),
    )


def _identificar(proposta):
    valor = proposta.get("id")
    if valor is None or str(valor).strip() == "":
        return SEM_ID
    return str(valor).strip()
