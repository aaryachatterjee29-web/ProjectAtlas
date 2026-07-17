"""Smoke tests for the Project Atlas backend entry point."""

from __future__ import annotations

import backend.main as backend_main


def test_main_prints_initialization_message(capsys: object) -> None:
    """The entry point's main() prints the expected initialization banner."""
    backend_main.main()
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    assert "Project Atlas initialized." in captured.out
