"""Keep real pipeline outputs in each test's temporary working directory."""
import pytest


@pytest.fixture(autouse=True)
def isolated_workdir(tmp_path, monkeypatch):
    (tmp_path / "debug").mkdir()
    monkeypatch.chdir(tmp_path)
    return tmp_path
