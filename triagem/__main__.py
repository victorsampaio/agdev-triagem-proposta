"""Linha de comando da triagem.

Uso:
    python -m triagem proposta.json
    python -m triagem proposta.json --formato json
    python -m triagem proposta.json --saida card.md
    python -m triagem < proposta.json
"""

import argparse
import json
import sys
from pathlib import Path

from triagem.card import gerar_card
from triagem.parecer import avaliar

CODIGO_ERRO_ENTRADA = 2


class ErroEntrada(Exception):
    pass


def ler_proposta(caminho):
    if caminho in (None, "-"):
        texto = sys.stdin.read()
    else:
        arquivo = Path(caminho)
        if not arquivo.is_file():
            raise ErroEntrada(f"arquivo não encontrado: {caminho}")
        try:
            texto = arquivo.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            raise ErroEntrada(f"o arquivo {caminho} não está em UTF-8. Salve-o em UTF-8 e tente de novo.")

    try:
        proposta = json.loads(texto.lstrip("\ufeff"))
    except json.JSONDecodeError as erro:
        raise ErroEntrada(f"JSON inválido (linha {erro.lineno}, coluna {erro.colno}): {erro.msg}.")

    if not isinstance(proposta, dict):
        raise ErroEntrada(
            "o JSON precisa ser um objeto com os campos da proposta, no formato {\"campo\": valor}."
        )
    return proposta


def _argumentos(argv):
    parser = argparse.ArgumentParser(
        prog="python -m triagem",
        description="Triagem de uma proposta da AgDev: parecer, motivos e pendências.",
    )
    parser.add_argument(
        "arquivo", nargs="?",
        help="arquivo JSON com a proposta. Sem arquivo (ou com -), lê da entrada padrão.",
    )
    parser.add_argument(
        "--formato", choices=["md", "json"], default="md",
        help="md: card em Markdown (padrão). json: parecer em JSON.",
    )
    parser.add_argument("--saida", help="grava o resultado neste arquivo, em UTF-8.")
    return parser.parse_args(argv)


def main(argv=None):
    args = _argumentos(argv)
    try:
        proposta = ler_proposta(args.arquivo)
    except ErroEntrada as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return CODIGO_ERRO_ENTRADA

    resultado = avaliar(proposta)
    if args.formato == "json":
        texto = json.dumps(resultado.como_dict(), ensure_ascii=False, indent=2) + "\n"
    else:
        texto = gerar_card(resultado)

    if args.saida is None:
        sys.stdout.write(texto)
        return 0
    try:
        Path(args.saida).write_text(texto, encoding="utf-8")
    except OSError as erro:
        print(f"Erro: não foi possível gravar {args.saida}: {erro.strerror}.", file=sys.stderr)
        return CODIGO_ERRO_ENTRADA
    print(f"Resultado gravado em {args.saida} (parecer: {resultado.parecer}).")
    return 0


if __name__ == "__main__":
    for fluxo in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")
    sys.exit(main())
