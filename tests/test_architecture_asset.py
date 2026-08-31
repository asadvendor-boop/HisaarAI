from pathlib import Path


def test_architecture_uses_wrapped_and_fitted_labels() -> None:
    source = (Path(__file__).parents[1] / "docs/media/architecture.svg").read_text()

    assert "App identity writes one receipt" in source
    assert "Separate identity • bounded evidence • never authorizes" in source
    assert "Bound through Firestore checkpoint mirror" in source
