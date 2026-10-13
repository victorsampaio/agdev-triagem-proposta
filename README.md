# Triagem de propostas - AgDev

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

## Premissas e decisões

O enunciado deixa alguns pontos em aberto. As dúvidas foram enviadas à AgDev por e-mail, e as respostas de 13/10/2026 estão marcadas abaixo. Cada decisão tem um teste automatizado que a comprova.

**Mudança de regra:** a AgDev informou que a data de corte da R2 é **01/01/2020**, e não 01/01/2021 como estava no enunciado.

| Regra | Decisão | Origem |
|---|---|---|
| R1 | Exatamente 100 ha passa. Área negativa ou que não seja número vai para revisão humana. | Enunciado e premissa |
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
