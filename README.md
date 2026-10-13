# Triagem de propostas - AgDev

[![testes](https://github.com/victorsampaio/agdev-triagem-proposta/actions/workflows/testes.yml/badge.svg)](https://github.com/victorsampaio/agdev-triagem-proposta/actions/workflows/testes.yml)

Skill do Claude (`triagem-proposta`) que faz a triagem de propostas de recuperação de pastagens degradadas e devolve um parecer: **SEGUE**, **RECUSADA** ou **REVISÃO HUMANA**, com todos os motivos.

> Em construção. As instruções completas de instalação e uso serão adicionadas.

## Rodar os testes

Pré-requisito: Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements-dev.txt
pytest
```

## Usar com o Claude Code

A skill fica em `.claude/skills/triagem-proposta/`, e o Claude Code a reconhece automaticamente quando é aberto na pasta do projeto.

```bash
cd agdev-triagem-proposta
claude
```

Depois, é só pedir em português. Por exemplo:

- "Faça a triagem da proposta exemplos/P-004.json."
- "Qual o parecer desta proposta?" seguido do JSON colado.
- "Proposta P-010: 250 ha de pastagem degradada, matrícula de 900 ha, CAR de 910 ha, CAR ativo, CPF regular."

O Claude não decide o parecer: ele roda o script da skill, que aplica as regras por código, e mostra o card sem alterações. Quando os dados vêm em texto livre, ele monta o JSON, mostra para você e pede confirmação antes de rodar. Propostas coladas na conversa são gravadas em `propostas/<id>.json` (pasta ignorada pelo git) antes da triagem. Por isso, o Claude Code pede permissão para gravar esse arquivo e para rodar o `python`. As instruções completas estão no [`SKILL.md`](.claude/skills/triagem-proposta/SKILL.md), e os testes feitos com o Claude Code estão registrados em [`docs/validacao-claude-code.md`](docs/validacao-claude-code.md).

## Usar pela linha de comando

Na pasta do projeto, com o ambiente virtual ativado:

```bash
python -m triagem exemplos/P-004.json                  # card em Markdown
python -m triagem exemplos/P-004.json --formato json   # parecer em JSON
python -m triagem exemplos/P-004.json --saida card.md  # grava o card em UTF-8
python -m triagem < exemplos/P-004.json                # lê a proposta da entrada padrão
```

No PowerShell, prefira `--saida` em vez de redirecionar com `>`, que grava em outra codificação e estraga os acentos.

Se o arquivo não existir, o JSON estiver quebrado ou não for um objeto, o comando mostra uma mensagem começando com `Erro:` e termina com código 2.

Card gerado para a proposta P-004:

```markdown
# Triagem P-004: RECUSADA

**Parecer:** RECUSADA

**Versão das regras:** 1.0.0

## Motivos

- **R2 (RECUSADA):** Alerta de desmatamento em 15/03/2023, posterior a 01/01/2020.
- **R3 (REVISÃO HUMANA):** Situação do CAR é "Pendente".

## Pendências

- [ ] Comunicar ao proponente a recusa: alerta de desmatamento posterior a 01/01/2020.
- [ ] Verificar com o proponente a regularização do CAR.

## Próximo passo

Comunicar a recusa ao proponente. A proposta não segue para o comitê.
```

## Premissas e decisões

O enunciado deixa alguns pontos em aberto. As dúvidas foram enviadas à AgDev por e-mail, e as respostas de 13/10/2026 estão marcadas abaixo. Cada decisão tem um teste automatizado que a comprova.

**Mudança de regra:** a AgDev informou que a data de corte da R2 é **01/01/2020**, e não 01/01/2021 como estava no enunciado.

| Regra | Decisão | Origem |
|---|---|---|
| R1 | Exatamente 100 ha passa. Área negativa ou que não seja número vai para revisão humana. | Enunciado e premissa |
| Áreas | As áreas devem vir como número (`850`). Área enviada como texto (`"850"`) é considerada inválida e vai para revisão humana. | Premissa |
| R2 | Alerta depois de 01/01/2020 recusa. Alerta no próprio dia 01/01/2020 não recusa. | Confirmado pela AgDev |
| R2 | O campo aceita nulo (sem alerta), uma data ou uma lista de datas. Lista vazia é sem alerta. Basta um alerta depois do corte para recusar. | Confirmado pela AgDev |
| R2 | Datas aceitas nos formatos `AAAA-MM-DD` e `DD/MM/AAAA`. Data inválida vai para revisão humana. | Premissa |
| R3 | Maiúsculas, minúsculas e espaços são ignorados. Valor fora da lista vai para revisão humana, citando o valor recebido. | Confirmado pela AgDev |
| R4 | Só "Regular" passa, inclusive para CNPJ. O tratamento dos status de CNPJ com dados reais está no `DESIGN.md`. | Confirmado pela AgDev |
| R5 | Diferença de exatamente 5% passa. A diferença é absoluta (CAR maior ou menor) e calculada sobre a área da matrícula, com números decimais exatos. | Enunciado e premissa |
| R5 | Sem a área da matrícula, a R5 não é avaliada e vira pendência. Matrícula igual a zero vai para revisão humana. | Premissa |
| R6 | Os 7 campos do formato sugerido são obrigatórios. | Confirmado pela AgDev |
| R6 | `alerta_desmatamento: null` significa sem alerta. Campo ausente vai para revisão humana. Nos demais campos, `null` conta como ausente. | Confirmado pela AgDev (nulo em outros campos: premissa) |
| Card | Motivos são as regras que falharam. Pendências são as ações concretas para resolver. Proposta com SEGUE não tem pendências. | Confirmado pela AgDev |
| Escopo | A skill aplica somente R1 a R6 e avalia uma proposta por vez. | Enunciado |
