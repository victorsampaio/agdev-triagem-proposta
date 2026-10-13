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
