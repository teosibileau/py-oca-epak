"""Simple import test to verify test setup."""


def test_import_ocaepak():
    """Verify ocaepak module can be imported."""
    from ocaepak.client import OcaService

    assert OcaService is not None
