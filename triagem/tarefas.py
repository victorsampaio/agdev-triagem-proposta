"""Integração simulada com um gerenciador de tarefas.

O quadro é uma pasta com um card em Markdown por proposta, um `quadro.json` com as
tarefas e um `quadro.md` para leitura. Para usar um gerenciador real (Asana, Trello,
TickTick), basta outra classe com o mesmo método `publicar(parecer)`.
"""

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from triagem.card import gerar_card
from triagem.parecer import SEM_ID
from triagem.regras import RECUSADA, REVISAO_HUMANA, SEGUE

PASTA_PADRAO = Path("saida") / "tarefas"
COLUNAS = {
    SEGUE: "Comitê de crédito",
    REVISAO_HUMANA: "Revisão humana",
    RECUSADA: "Recusadas",
}


class ErroPublicacao(Exception):
    pass


@dataclass(frozen=True)
class Tarefa:
    id: str
    titulo: str
    coluna: str
    parecer: str
    arquivo: str
    versao_regras: str
    atualizada_em: str


class QuadroSimulado:
    def __init__(self, pasta=PASTA_PADRAO):
        self.pasta = Path(pasta)

    @property
    def arquivo_quadro(self):
        return self.pasta / "quadro.json"

    def tarefas(self):
        if not self.arquivo_quadro.is_file():
            return []
        try:
            dados = json.loads(self.arquivo_quadro.read_text(encoding="utf-8"))
            return [Tarefa(**item) for item in dados["tarefas"]]
        except (ValueError, KeyError, TypeError):
            raise ErroPublicacao(f"o quadro {self.arquivo_quadro} está corrompido. Apague o arquivo e publique de novo.")

    def publicar(self, parecer, agora=None):
        """Cria ou atualiza a tarefa da proposta. Devolve a tarefa e se ela é nova."""
        if parecer.id_proposta == SEM_ID:
            raise ErroPublicacao("a proposta precisa de um id para virar tarefa.")

        tarefa = Tarefa(
            id=parecer.id_proposta,
            titulo=f"Triagem {parecer.id_proposta}: {parecer.parecer}",
            coluna=COLUNAS[parecer.parecer],
            parecer=parecer.parecer,
            arquivo=_nome_do_arquivo(parecer.id_proposta),
            versao_regras=parecer.versao_regras,
            atualizada_em=(agora or datetime.now()).isoformat(timespec="seconds"),
        )
        existentes = self.tarefas()
        for outra in existentes:
            if outra.arquivo == tarefa.arquivo and outra.id != tarefa.id:
                raise ErroPublicacao(
                    f"os ids {outra.id!r} e {tarefa.id!r} gerariam o mesmo arquivo ({tarefa.arquivo})."
                )
        nova = all(outra.id != tarefa.id for outra in existentes)
        tarefas = [outra for outra in existentes if outra.id != tarefa.id] + [tarefa]

        try:
            self.pasta.mkdir(parents=True, exist_ok=True)
            (self.pasta / tarefa.arquivo).write_text(gerar_card(parecer), encoding="utf-8", newline="\n")
            self.arquivo_quadro.write_text(
                json.dumps({"tarefas": [asdict(t) for t in tarefas]}, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            (self.pasta / "quadro.md").write_text(_quadro_em_markdown(tarefas), encoding="utf-8", newline="\n")
        except OSError as erro:
            raise ErroPublicacao(f"não foi possível gravar no quadro {self.pasta}: {erro.strerror}.")
        return tarefa, nova


def _nome_do_arquivo(id_proposta):
    return re.sub(r"[^\w.-]", "_", id_proposta) + ".md"


def _quadro_em_markdown(tarefas):
    linhas = ["# Quadro de tarefas da triagem", ""]
    for coluna in COLUNAS.values():
        linhas += [f"## {coluna}", ""]
        da_coluna = [t for t in tarefas if t.coluna == coluna]
        if da_coluna:
            linhas += [f"- [{t.titulo}]({t.arquivo}) (atualizada em {t.atualizada_em})" for t in da_coluna]
        else:
            linhas.append("Nenhuma tarefa.")
        linhas.append("")
    return "\n".join(linhas)
