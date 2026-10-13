"""Atalho da skill: roda a triagem (python -m triagem) a partir de qualquer pasta.

Procura o pacote `triagem` ao lado da skill ou nas pastas acima dela (raiz do repositório).
"""

import runpy
import sys
from pathlib import Path

PASTA_SKILL = Path(__file__).resolve().parent.parent

for pasta in (PASTA_SKILL, *PASTA_SKILL.parents):
    if (pasta / "triagem" / "regras.py").is_file():
        sys.path.insert(0, str(pasta))
        break
else:
    sys.exit("Erro: não encontrei o pacote 'triagem' (código das regras) perto desta skill.")

runpy.run_module("triagem", run_name="__main__", alter_sys=True)
