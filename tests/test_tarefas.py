import io
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

from triagem import avaliar
from triagem.__main__ import CODIGO_ERRO_ENTRADA, main
from triagem.card import gerar_card
from triagem.tarefas import ErroPublicacao, QuadroSimulado

RAIZ = Path(__file__).resolve().parent.parent
AGORA = datetime(2026, 10, 14, 9, 30)


def exemplo(id_proposta):
    return json.loads((RAIZ / "exemplos" / f"{id_proposta}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("id_proposta, coluna", [
    ("P-001", "Comitê de crédito"),
    ("P-002", "Recusadas"),
    ("P-003", "Revisão humana"),
])
def test_tarefa_vai_para_a_coluna_do_parecer(tmp_path, id_proposta, coluna):
    tarefa, nova = QuadroSimulado(tmp_path).publicar(avaliar(exemplo(id_proposta)), agora=AGORA)

    assert nova
    assert tarefa.coluna == coluna
    assert tarefa.atualizada_em == "2026-10-14T09:30:00"


def test_card_da_tarefa_e_o_mesmo_do_parecer_em_utf8(tmp_path):
    parecer = avaliar(exemplo("P-005"))

    tarefa, _ = QuadroSimulado(tmp_path).publicar(parecer)

    assert (tmp_path / tarefa.arquivo).read_bytes().decode("utf-8") == gerar_card(parecer)


def test_triar_de_novo_atualiza_a_tarefa_sem_duplicar(tmp_path, proposta):
    quadro = QuadroSimulado(tmp_path)
    quadro.publicar(avaliar(proposta(sem=("area_matricula_ha",))))

    tarefa, nova = quadro.publicar(avaliar(proposta()))

    assert not nova
    assert [t.id for t in quadro.tarefas()] == ["P-TESTE"]
    assert tarefa.coluna == "Comitê de crédito"
    assert "SEGUE" in (tmp_path / tarefa.arquivo).read_text(encoding="utf-8")


def test_quadro_em_markdown_lista_cada_tarefa_na_sua_coluna(tmp_path):
    quadro = QuadroSimulado(tmp_path)
    for id_proposta in ("P-001", "P-002", "P-003", "P-004", "P-005"):
        quadro.publicar(avaliar(exemplo(id_proposta)))

    texto = (tmp_path / "quadro.md").read_text(encoding="utf-8")
    comite, revisao, recusadas = (
        texto.split("## Comitê de crédito")[1].split("## Revisão humana")[0],
        texto.split("## Revisão humana")[1].split("## Recusadas")[0],
        texto.split("## Recusadas")[1],
    )

    assert len(quadro.tarefas()) == 5
    assert "P-001" in comite
    assert "P-003" in revisao and "P-005" in revisao
    assert "P-002" in recusadas and "P-004" in recusadas


def test_proposta_sem_id_nao_vira_tarefa(tmp_path, proposta):
    with pytest.raises(ErroPublicacao, match="precisa de um id"):
        QuadroSimulado(tmp_path).publicar(avaliar(proposta(sem=("id",))))


def test_id_com_caracteres_especiais_vira_nome_de_arquivo_seguro(tmp_path, proposta):
    tarefa, _ = QuadroSimulado(tmp_path).publicar(avaliar(proposta(id="P/010 a")))

    assert tarefa.arquivo == "P_010_a.md"
    assert (tmp_path / "P_010_a.md").is_file()


def test_ids_que_gerariam_o_mesmo_arquivo_sao_recusados(tmp_path, proposta):
    quadro = QuadroSimulado(tmp_path)
    quadro.publicar(avaliar(proposta(id="P/010")))

    with pytest.raises(ErroPublicacao, match="mesmo arquivo"):
        quadro.publicar(avaliar(proposta(id="P_010")))


def test_quadro_corrompido_tem_mensagem_clara(tmp_path, proposta):
    (tmp_path / "quadro.json").write_text("isto não é JSON", encoding="utf-8")

    with pytest.raises(ErroPublicacao, match="corrompido"):
        QuadroSimulado(tmp_path).publicar(avaliar(proposta()))


def test_linha_de_comando_publica_e_mantem_o_card_na_saida(tmp_path, capsys):
    codigo = main([str(RAIZ / "exemplos" / "P-004.json"), "--publicar", "--quadro", str(tmp_path)])
    saida = capsys.readouterr()

    assert codigo == 0
    assert saida.out.startswith("# Triagem P-004: RECUSADA")
    assert "Tarefa criada no quadro" in saida.err
    assert "coluna Recusadas" in saida.err
    assert (tmp_path / "P-004.md").is_file()


def test_linha_de_comando_com_json_continua_gerando_json_valido(tmp_path, capsys):
    main([str(RAIZ / "exemplos" / "P-004.json"), "--formato", "json", "--publicar", "--quadro", str(tmp_path)])

    assert json.loads(capsys.readouterr().out)["parecer"] == "RECUSADA"


def test_linha_de_comando_avisa_quando_a_tarefa_e_atualizada(tmp_path, capsys):
    argumentos = [str(RAIZ / "exemplos" / "P-004.json"), "--publicar", "--quadro", str(tmp_path)]
    main(argumentos)
    capsys.readouterr()

    main(argumentos)

    assert "Tarefa atualizada no quadro" in capsys.readouterr().err


def test_linha_de_comando_sem_id_da_erro_claro(tmp_path, monkeypatch, capsys, proposta):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(proposta(sem=("id",)))))

    codigo = main(["--publicar", "--quadro", str(tmp_path)])

    assert codigo == CODIGO_ERRO_ENTRADA
    assert "Erro: a proposta precisa de um id" in capsys.readouterr().err


def test_sem_publicar_nada_e_gravado(tmp_path, capsys):
    main([str(RAIZ / "exemplos" / "P-004.json"), "--quadro", str(tmp_path)])

    assert list(tmp_path.iterdir()) == []
