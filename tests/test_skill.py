import json
import re
import subprocess
import sys
from pathlib import Path

from triagem import SEGUE, VERSAO_REGRAS, avaliar
from triagem.regras import AREA_MINIMA_HA, DATA_CORTE_DESMATAMENTO, TOLERANCIA_DIFERENCA_AREA

RAIZ = Path(__file__).resolve().parent.parent
PASTA_SKILL = RAIZ / ".claude" / "skills" / "triagem-proposta"
SKILL_MD = (PASTA_SKILL / "SKILL.md").read_text(encoding="utf-8")
ATALHO = PASTA_SKILL / "scripts" / "triagem.py"


def cabecalho():
    assert SKILL_MD.startswith("---\n")
    bloco = SKILL_MD.split("---\n", 2)[1]
    return dict(linha.split(": ", 1) for linha in bloco.strip().splitlines())


def test_cabecalho_tem_nome_igual_ao_da_pasta():
    nome = cabecalho()["name"]

    assert nome == PASTA_SKILL.name
    assert re.fullmatch(r"[a-z0-9-]{1,64}", nome)


def test_descricao_diz_quando_usar_e_cabe_no_limite():
    descricao = cabecalho()["description"]

    assert 0 < len(descricao) <= 1024
    assert "Use quando" in descricao


def test_skill_md_esta_alinhado_com_os_parametros_do_codigo():
    assert f"Versão das regras: {VERSAO_REGRAS}." in SKILL_MD
    assert f"pelo menos {AREA_MINIMA_HA} ha" in SKILL_MD
    assert f"depois de {DATA_CORTE_DESMATAMENTO:%d/%m/%Y}" in SKILL_MD
    assert f"acima de {TOLERANCIA_DIFERENCA_AREA * 100:.0f}%" in SKILL_MD


def test_exemplos_json_do_skill_md_sao_validos_e_seguem():
    exemplos = re.findall(r"^\s*(\{\"id\".*\})\s*$", SKILL_MD, flags=re.MULTILINE)

    assert len(exemplos) == 2
    for exemplo in exemplos:
        assert avaliar(json.loads(exemplo)).parecer == SEGUE


def executar_atalho(*argumentos, entrada=None, pasta=None):
    return subprocess.run(
        [sys.executable, str(ATALHO), *argumentos],
        cwd=pasta, input=entrada, capture_output=True, check=False,
    )


def test_atalho_funciona_de_outra_pasta_com_arquivo(tmp_path):
    processo = executar_atalho(str(RAIZ / "exemplos" / "P-005.json"), pasta=tmp_path)

    assert processo.returncode == 0
    assert processo.stdout.decode("utf-8").startswith("# Triagem P-005: REVISÃO HUMANA")


def test_atalho_le_a_proposta_pela_entrada_padrao(tmp_path):
    entrada = (RAIZ / "exemplos" / "P-004.json").read_bytes()

    processo = executar_atalho("--formato", "json", entrada=entrada, pasta=tmp_path)

    assert processo.returncode == 0
    assert json.loads(processo.stdout.decode("utf-8"))["parecer"] == "RECUSADA"


def test_atalho_repassa_erro_de_entrada(tmp_path):
    processo = executar_atalho("nao-existe.json", pasta=tmp_path)

    assert processo.returncode == 2
    assert processo.stderr.decode("utf-8").startswith("Erro: arquivo não encontrado")
