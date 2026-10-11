"""
fixtures.py — récupère le catalogue d'outils en interrogeant les VRAIS serveurs MCP.

Aucun outil n'est écrit en dur. Chaque serveur est lancé comme un vrai
sous-processus MCP (stdio) via client.get_tools(), exactement comme le ferait
un agent, et on récupère ce qu'il annonce (nom + description).

Serveurs interrogés : uniquement les serveurs d'attaque attacks/evil_*.py.

Le scanner ne reçoit AUCUNE étiquette « piégé » / « sain » : c'est à lui de décider.
"""

from __future__ import annotations

import sys
from pathlib import Path

from client import get_tools

ROOT = Path(__file__).resolve().parent


def server_paths() -> list[Path]:
    """Liste des fichiers serveurs MCP à interroger : attacks/evil_*.py."""
    return sorted((ROOT / "attacks").glob("evil_*.py"))


def load_catalogue_with_errors() -> tuple[list[dict], list[tuple[str, str]]]:
    """Interroge chaque serveur MCP. Renvoie (outils, erreurs).

    outils  : [{"name", "description", "server"}, ...] tels qu'annoncés par les serveurs
    erreurs : [(nom_du_serveur, message), ...] pour les serveurs injoignables
    """
    tools: list[dict] = []
    errors: list[tuple[str, str]] = []
    for path in server_paths():
        try:
            for t in get_tools(str(path)):
                tools.append({
                    "name": t["name"],
                    "description": t["description"],
                    "server": path.stem,
                })
        except Exception as exc:  # serveur qui ne démarre pas : on le signale, on continue
            errors.append((path.stem, f"{type(exc).__name__}: {exc}"))
    return tools, errors


def load_catalogue() -> list[dict]:
    """Comme load_catalogue_with_errors, mais affiche les erreurs dans le terminal."""
    tools, errors = load_catalogue_with_errors()
    for server, msg in errors:
        print(f"[SERVEUR MCP INJOIGNABLE] {server} : {msg}", file=sys.stderr, flush=True)
    return tools


if __name__ == "__main__":
    for t in load_catalogue():
        print(f"{t['server']:16} {t['name']:24} :: {t['description'][:60]}…")
