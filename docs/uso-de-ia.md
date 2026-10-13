# Registro de uso de IA

Como a IA foi usada em cada etapa do teste, o que foi decidido por mim e o que precisou ser corrigido. O resumo está na seção 5 do [`DESIGN.md`](../DESIGN.md).

**Ferramentas:** agente do Cursor (código, testes e documentos) e Claude Code 2.1.296 (validação da skill).

| Etapa | O que a IA fez | O que eu decidi ou revisei |
|---|---|---|
| Entendimento | Transcreveu o PDF do enunciado para Markdown e montou uma estratégia em fases. | Notei acentos trocados por "?" na transcrição e pedi a correção. Revisei as fases e passei a conduzir o trabalho fase a fase. |
| Dúvidas | Listou 17 ambiguidades das regras (fronteiras, nulo × ausente, CPF × CNPJ, vários alertas). | Decidi perguntar à AgDev antes de programar e enviei o e-mail. A resposta mudou a data de corte da R2 para 01/01/2020. |
| Ambiente | Sugeriu Python sem dependências externas, com pytest e CI no GitHub. | Escolhi o local do projeto, o repositório público e a instalação do Python e do GitHub CLI. |
| Regras e testes | Escreveu as regras R1 a R6, a consolidação do parecer e os testes de borda. | Revisei os resultados esperados dos 5 exemplos e as premissas de cada regra. |
| Card e linha de comando | Escreveu o card em Markdown e o comando `python -m triagem`. | Conferi os cards gerados para os 5 exemplos. |
| Skill do Claude | Escreveu o `SKILL.md`, o script da skill e rodou a validação no Claude Code. | Autorizei o uso da minha conta do Claude para os testes e deixei o Claude Desktop para depois. |
| Documentação | Escreveu os rascunhos do README, deste registro, do `DESIGN.md` e do `CHANGELOG.md`. | Revisei e ajustei os textos. As respostas do `PERGUNTAS.md` são minhas. |

Toda publicação no repositório (push para o `main`) passou pela minha aprovação.

## Como conferi o que a IA produziu

- **Testes automáticos:** 137 testes, incluindo fronteiras (exatamente 100 ha, exatamente 5%, alerta no dia do corte) e entradas inválidas. Rodam no CI em Python 3.10 e 3.12.
- **Teste de mutação:** foram inseridos 4 erros de propósito no código (trocar `>` por `>=` na R5 e na R2, trocar `<` por `<=` na R1 e voltar a data de corte para 2021). Os testes pegaram os 4.
- **Validação real no Claude Code:** 5 pedidos, incluindo texto livre incompleto e um pedido para ignorar a R2. A validação achou um erro na primeira versão da skill, já corrigido. Registro em [`validacao-claude-code.md`](validacao-claude-code.md).

## O que deu errado e como foi corrigido

- **Acentuação:** a ferramenta de edição às vezes gravava os arquivos em outra codificação, e os acentos quebravam. Passei a conferir a codificação UTF-8 de cada arquivo depois de editar.
- **Skill com JSON no comando:** a primeira versão do `SKILL.md` mandava o Claude passar o JSON dentro do comando, e o Claude Code bloqueia isso. A skill passou a gravar a proposta num arquivo antes de rodar o script.
- **Python no PATH:** na primeira validação, o Claude Code encontrou o atalho do Python da Microsoft Store em vez do Python instalado. Era um problema do ambiente de teste; o README agora explica como evitar.
