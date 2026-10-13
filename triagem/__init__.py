"""Triagem de propostas de recuperação de pastagens degradadas (AgDev)."""

from triagem.parecer import Parecer, avaliar
from triagem.regras import RECUSADA, REVISAO_HUMANA, SEGUE, VERSAO_REGRAS

__all__ = ["Parecer", "avaliar", "RECUSADA", "REVISAO_HUMANA", "SEGUE", "VERSAO_REGRAS"]
