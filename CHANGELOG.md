# Histórico de versões

As versões seguem a constante `VERSAO_REGRAS` em `triagem/regras.py`, que aparece em todo card e em todo parecer.

- **Versão maior (2.0.0):** muda o parecer de alguma proposta. Exemplos: regra nova ou removida, data de corte, área mínima ou tolerância diferentes.
- **Versão menor (1.1.0):** novidade que não muda nenhum parecer. Exemplo: novo formato de saída.
- **Correção (1.0.1):** ajuste de texto ou correção de falha. Se a correção mudar algum parecer, o comitê precisa ser avisado.

## 1.0.0 - 2026-10-14

Primeira versão.

### Regras

- R1: área degradada de pelo menos 100 ha; abaixo disso, RECUSADA.
- R2: alerta de desmatamento depois de 01/01/2020, RECUSADA. A data de corte foi informada pela AgDev e substitui 01/01/2021, que constava no enunciado.
- R3: CAR "Ativo" segue; "Pendente" ou valor desconhecido, REVISÃO HUMANA; "Cancelado" ou "Suspenso", RECUSADA.
- R4: situação cadastral diferente de "Regular", REVISÃO HUMANA.
- R5: diferença entre a área da matrícula e a do CAR acima de 5% da matrícula, REVISÃO HUMANA.
- R6: campo obrigatório ausente, REVISÃO HUMANA, citando o campo.
- RECUSADA prevalece sobre REVISÃO HUMANA, que prevalece sobre SEGUE. Todos os motivos são listados.

### Recursos

- Card em Markdown com parecer, motivos, pendências e próximo passo.
- Linha de comando `python -m triagem`, com saída em Markdown ou JSON.
- Integração simulada com um gerenciador de tarefas (`--publicar`): o card vira uma tarefa num quadro local, na coluna do parecer.
- Skill `triagem-proposta` para o Claude Code, validada com 7 pedidos.
- Testes automatizados com casos de borda, rodando no CI em Python 3.10 e 3.12.
