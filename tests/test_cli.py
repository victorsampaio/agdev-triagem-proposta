import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

from triagem.__main__ import CODIGO_ERRO_ENTRADA, main

RAIZ = Path(__file__).resolve().parent.parent
P004 = str(RAIZ / "exemplos" / "P-004.json")
P005 = str(RAIZ / "exemplos" / "P-005.json")


def test_card_em_markdown_e_o_formato_padrao(capsys):
    codigo = main([P004])
    saida = capsys.readouterr().out

    assert codigo == 0
    assert saida.startswith("# Triagem P-004: RECUSADA")


def test_formato_json_gera_json_valido(capsys):
    codigo = main([P004, "--formato", "json"])
    dados = json.loads(capsys.readouterr().out)

    assert codigo == 0
    assert dados["id"] == "P-004"
    assert dados["parecer"] == "RECUSADA"
    assert [m["regra"] for m in dados["motivos"]] == ["R2", "R3"]


@pytest.mark.parametrize("argumentos", [[], ["-"]], ids=["sem-arquivo", "hifen"])
def test_le_a_proposta_pela_entrada_padrao(argumentos, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO(Path(P005).read_text(encoding="utf-8")))

    codigo = main(argumentos)

    assert codigo == 0
    assert capsys.readouterr().out.startswith("# Triagem P-005: REVISÃO HUMANA")


def test_saida_grava_o_resultado_em_utf8(tmp_path, capsys):
    destino = tmp_path / "card.md"

    codigo = main([P004, "--saida", str(destino)])

    assert codigo == 0
    assert "REVISÃO HUMANA" in destino.read_bytes().decode("utf-8")
    assert "parecer: RECUSADA" in capsys.readouterr().out


def test_arquivo_com_bom_e_aceito(tmp_path, capsys):
    arquivo = tmp_path / "proposta.json"
    arquivo.write_text(Path(P005).read_text(encoding="utf-8"), encoding="utf-8-sig")

    assert main([str(arquivo)]) == 0
    assert "P-005" in capsys.readouterr().out


@pytest.mark.parametrize("conteudo, trecho_da_mensagem", [
    pytest.param(None, "arquivo não encontrado", id="arquivo-inexistente"),
    pytest.param(b'{"id": "P-1",', "JSON inválido (linha 1", id="json-quebrado"),
    pytest.param(b"[]", "precisa ser um objeto", id="json-que-nao-e-objeto"),
    pytest.param("{\"situacao_cadastral\": \"regularização\"}".encode("cp1252"), "não está em UTF-8", id="arquivo-fora-de-utf8"),
])
def test_erros_de_entrada_tem_mensagem_clara_e_codigo_2(tmp_path, capsys, conteudo, trecho_da_mensagem):
    arquivo = tmp_path / "proposta.json"
    if conteudo is not None:
        arquivo.write_bytes(conteudo)

    codigo = main([str(arquivo)])
    erro = capsys.readouterr().err

    assert codigo == CODIGO_ERRO_ENTRADA
    assert erro.startswith("Erro: ")
    assert trecho_da_mensagem in erro
    assert "Traceback" not in erro


def test_erro_ao_gravar_a_saida_tem_mensagem_clara(tmp_path, capsys):
    destino = tmp_path / "pasta-que-nao-existe" / "card.md"

    codigo = main([P004, "--saida", str(destino)])

    assert codigo == CODIGO_ERRO_ENTRADA
    assert capsys.readouterr().err.startswith("Erro: não foi possível gravar")


def executar(*argumentos, entrada=None):
    return subprocess.run(
        [sys.executable, "-m", "triagem", *argumentos],
        cwd=RAIZ, input=entrada, capture_output=True, check=False,
    )


def test_python_m_triagem_funciona_e_escreve_em_utf8():
    processo = executar(P005)
    saida = processo.stdout.decode("utf-8")

    assert processo.returncode == 0
    assert "# Triagem P-005: REVISÃO HUMANA" in saida
    assert "Pendente de regularização" in saida


def test_python_m_triagem_le_utf8_pela_entrada_padrao():
    processo = executar("--formato", "json", entrada=Path(P005).read_bytes())
    dados = json.loads(processo.stdout.decode("utf-8"))

    assert processo.returncode == 0
    assert dados["parecer"] == "REVISÃO HUMANA"
    assert "\"Pendente de regularização\"" in dados["motivos"][0]["mensagem"]
