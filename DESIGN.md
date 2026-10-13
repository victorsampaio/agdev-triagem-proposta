# Desenho da solução

Princípio: **o código decide, o Claude conversa e o humano revisa.**

## 1. Onde entra a revisão humana, e por quê

- **Pela regra:** CAR pendente (R3), CPF/CNPJ fora de "Regular" (R4), áreas divergentes (R5) e campo ausente (R6).
- **Por dado não confiável:** valor desconhecido, dado inválido ou, com dados reais, fonte fora do ar. Dado ruim nunca vira SEGUE.
- **Antes e depois:** o analista confirma o JSON que o Claude montou a partir de texto livre. SEGUE só libera para o comitê. Exceção a uma RECUSADA é decisão de pessoas, nunca do Claude.

Por quê: o julgamento fica com quem responde por ele, e deixar passar um caso ruim custa mais do que revisar um caso a mais.

## 2. Dados reais e o que pode dar errado

Cada fonte vira um coletor que preenche o mesmo JSON, com fonte e data; as regras não mudam.

| Fonte | O que pode dar errado |
|---|---|
| SICAR (situação e área do CAR) | Consulta instável, dado desatualizado, CAR de outro imóvel. |
| PRODES/DETER ou MapBiomas Alerta | Falso positivo na borda do polígono; exige área mínima de sobreposição. |
| Receita Federal (Serpro) | Custo por consulta, limite de chamadas, LGPD. |

**CNPJ:** a Receita usa outros termos (Ativa, Suspensa, Inapta, Baixada, Nula). Eu trataria "Ativa" como "Regular" e as demais como revisão humana; recusar direto alguma delas é decisão do comitê.

## 3. Quando o comitê muda uma regra

Os parâmetros ficam num lugar só, e a mudança entra por pull request, com teste na fronteira, aprovação de negócio e CI verde. A versão (`VERSAO_REGRAS`) sobe conforme o `CHANGELOG.md` e vira uma tag; o time atualiza com `git pull`. Cada card mostra a versão usada. Neste teste, a data de corte da R2 mudou de 2021 para 2020: bastou um parâmetro e os testes de fronteira.

## 4. Como o analista passa a usar e a confiar

Ele pede a triagem em português e recebe um card com o motivo de cada regra e o próximo passo. No início, a triagem roda em paralelo com a manual, e cada divergência vira um teste. O Claude não muda o parecer, e o analista sempre pode pedir revisão.

## 5. Como usei IA

O agente do Cursor escreveu código, testes e rascunhos. Eu decidi consultar a AgDev, revisei cada fase e conferi tudo com testes e uma validação real no Claude Code (`docs/uso-de-ia.md`).
