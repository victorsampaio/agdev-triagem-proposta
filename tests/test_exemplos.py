import json
from pathlib import Path

import pytest

EXEMPLOS = sorted((Path(__file__).resolve().parent.parent / "exemplos").glob("P-*.json"))


def test_existem_os_cinco_exemplos_do_enunciado():
    assert [arquivo.stem for arquivo in EXEMPLOS] == ["P-001", "P-002", "P-003", "P-004", "P-005"]


@pytest.mark.parametrize("arquivo", EXEMPLOS, ids=lambda arquivo: arquivo.stem)
def test_exemplo_e_json_valido_em_utf8(arquivo):
    proposta = json.loads(arquivo.read_text(encoding="utf-8"))
    assert proposta["id"] == arquivo.stem
