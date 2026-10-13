"""Resumo do parecer em Markdown, pronto para virar um card de tarefa."""

from triagem.regras import RECUSADA, REVISAO_HUMANA, SEGUE

PROXIMO_PASSO = {
    SEGUE: "Encaminhar a proposta ao comitê de crédito. SEGUE não é aprovação de crédito.",
    REVISAO_HUMANA: "Um analista resolve as pendências e roda a triagem de novo.",
    RECUSADA: "Comunicar a recusa ao proponente. A proposta não segue para o comitê.",
}


def gerar_card(parecer):
    linhas = [
        f"# Triagem {parecer.id_proposta}: {parecer.parecer}",
        "",
        f"**Parecer:** {parecer.parecer}",
        "",
        f"**Versão das regras:** {parecer.versao_regras}",
        "",
        "## Motivos",
        "",
    ]
    if parecer.motivos:
        linhas += [f"- **{m.regra} ({m.resultado}):** {m.mensagem}" for m in parecer.motivos]
    else:
        linhas.append("Nenhum motivo: a proposta atende às regras R1 a R6.")

    linhas += ["", "## Pendências", ""]
    if parecer.pendencias:
        linhas += [f"- [ ] {p}" for p in parecer.pendencias]
    else:
        linhas.append("Nenhuma pendência.")

    linhas += ["", "## Próximo passo", "", PROXIMO_PASSO[parecer.parecer]]
    return "\n".join(linhas) + "\n"
