"""Real debug writes must stay in the current test's temporary directory."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


CT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CT))


@pytest.fixture(scope="module", autouse=True)
def protected_checkout(tmp_path_factory):
    # A synthetic checkout makes the pre-isolation RED safe for real artifacts.
    directory = tmp_path_factory.mktemp("synthetic-checkout")
    debug = directory / "debug"
    debug.mkdir()
    with pytest.MonkeyPatch.context() as patch:
        patch.chdir(directory)
        yield directory
        assert Path.cwd() == directory


@pytest.fixture
def protected_outputs(protected_checkout):
    # Refresh only fixture-owned sentinels so each parametrized case is independent.
    sentinels = {}
    for name in ("debug.f_distribution.json.dump", "error.txt"):
        path = protected_checkout / "debug" / name
        path.write_bytes(b"preserve this fixture artifact\n")
        sentinels[path] = (path.read_bytes(), path.stat().st_mtime_ns)
    return sentinels


@pytest.mark.parametrize("operation", ["direct", "subprocess"])
def test_real_distribution_writes_preserve_other_workdirs(
        protected_outputs, tmp_path, operation):
    faces = [[(0, 1), (1, 0)] for _ in range(3)]
    if operation == "direct":
        spec = importlib.util.spec_from_file_location("fourct_isolation", CT / "4ct.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.stats = {}
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        assert mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_positive_corner) == []
    else:
        source = tmp_path / "theta.planar"
        source.write_text(json.dumps(faces) + "\n")
        result = subprocess.run(
            [sys.executable, str(CT / "4ct.py"), "-s5", "-p", str(source)],
            cwd=Path.cwd(), capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr

    for path, expected in protected_outputs.items():
        assert (path.read_bytes(), path.stat().st_mtime_ns) == expected
    distribution = tmp_path / "debug" / "debug.f_distribution.json.dump"
    assert json.loads(distribution.read_text()) == {"2": 3}
    assert Path.cwd() == tmp_path
