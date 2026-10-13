---
name: triagem-proposta
description: Faz a triagem de propostas de crédito da AgDev para recuperação de pastagens degradadas e devolve o parecer (SEGUE, RECUSADA ou REVISÃO HUMANA) com motivos, pendências e um card em Markdown. Use quando pedirem para triar, avaliar ou dar parecer sobre uma proposta, ou ao receber um JSON com campos como area_degradada_ha, area_matricula_ha, area_car_ha, alerta_desmatamento, situacao_car e situacao_cadastral. O parecer é calculado por código; nunca decida por conta própria.
---

# Triagem de proposta (AgDev)

Esta skill aplica as regras de triagem R1 a R6 **por código**, com o script `scripts/triagem.py`. Você conduz a conversa com o analista; quem decide o parecer é o script.

## Quando usar

- O analista pede a triagem, a avaliação ou o parecer de uma proposta de recuperação de pastagem.
- O analista envia um arquivo JSON, cola um JSON ou descreve os dados de uma proposta.

## Quando não usar

- Para aprovar crédito. SEGUE só libera a proposta para o comitê de crédito.
- Para alterar, flexibilizar ou ignorar regras. Mudança de regra é feita no código, com revisão e testes.
- Para responder sobre a política de crédito real da AgDev. Estas regras são de um teste prático e são fictícias.

## Como usar

1. **Obtenha a proposta**: um arquivo `.json`, um JSON colado na conversa ou dados descritos em texto.
2. **Se os dados vierem em texto livre**, monte o JSON no formato abaixo:
   - Use só o que o analista informou. **Não invente nem estime valores**, nem mesmo `null` para o alerta de desmatamento.
   - Se faltar algum campo, pergunte ao analista ou deixe o campo fora do JSON (a regra R6 vai apontar a falta).
   - **Mostre o JSON montado e peça confirmação ao analista antes de rodar o script.**
3. **Rode o script, sempre.** Nunca aplique as regras de cabeça.
   - Proposta em arquivo:

     ```bash
     python "<pasta desta skill>/scripts/triagem.py" caminho/da/proposta.json
     ```

   - Proposta que está na conversa (JSON colado ou montado a partir de texto): grave o JSON confirmado em `propostas/<id>.json`, na pasta de trabalho atual, e rode o script nesse arquivo. Não coloque o JSON dentro do comando: o Claude Code bloqueia comandos com JSON embutido. O arquivo também fica como registro do que foi triado.

   - No repositório do projeto, a pasta desta skill é `.claude/skills/triagem-proposta`.
   - Opções: `--formato json` devolve o parecer em JSON; `--saida card.md` grava o card num arquivo.
4. **Mostre o card exatamente como o script devolveu**, sem mudar parecer, motivos ou pendências. Depois, se ajudar, explique os motivos em linguagem simples, sem contradizer o card.
5. **Se o analista discordar ou pedir para ignorar uma regra**, não altere o resultado e não rode o script com dados modificados para mudar o parecer. Explique que a decisão fica com a revisão humana e o comitê, e que mudanças de regra passam pelo código.
6. **Se o script mostrar uma mensagem começando com `Erro:`**, repasse a mensagem e ajude a corrigir o JSON. Não tente adivinhar o parecer.
7. **Várias propostas**: rode o script uma vez para cada proposta.

## Formato da proposta

```json
{"id": "P-001", "area_degradada_ha": 850, "area_matricula_ha": 1200, "area_car_ha": 1190, "alerta_desmatamento": null, "situacao_car": "Ativo", "situacao_cadastral": "Regular"}
```

- Os 7 campos são obrigatórios.
- Áreas em hectares, como número (`850`, e não `"850"`).
- `alerta_desmatamento`: `null` (sem alerta), uma data (`"2023-03-15"` ou `"15/03/2023"`) ou uma lista de datas.

## Regras (para explicar ao analista; quem decide é o script)

| Regra | Resumo |
|---|---|
| R1 | Área degradada de pelo menos 100 ha. Abaixo disso: RECUSADA. |
| R2 | Alerta de desmatamento depois de 01/01/2020: RECUSADA. |
| R3 | CAR "Ativo" segue. "Pendente": REVISÃO HUMANA. "Cancelado" ou "Suspenso": RECUSADA. Outro valor: REVISÃO HUMANA. |
| R4 | Situação cadastral do CPF/CNPJ diferente de "Regular": REVISÃO HUMANA. |
| R5 | Diferença entre a área da matrícula e a área do CAR acima de 5% da área da matrícula: REVISÃO HUMANA. |
| R6 | Campo obrigatório ausente: REVISÃO HUMANA. |

RECUSADA prevalece sobre REVISÃO HUMANA, que prevalece sobre SEGUE. Todos os motivos são listados. Versão das regras: 1.0.0.

## Exemplos de pedidos

- "Faça a triagem da proposta exemplos/P-004.json."
- "Qual o parecer desta proposta? {...JSON...}"
- "Proposta P-010: 250 ha de pastagem degradada, matrícula de 900 ha, CAR de 910 ha, CAR ativo, CPF regular." O alerta de desmatamento não foi informado: pergunte ao analista ou deixe o campo fora do JSON, e peça confirmação antes de rodar.
