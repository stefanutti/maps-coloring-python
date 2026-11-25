"""The final statistics omit counters of the strategies that are not in use."""
import importlib.util
import logging
from pathlib import Path
import sys

import pytest


CT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CT))


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("fourct_stats", CT / "4ct.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.stats = {}
    module.initialize_statistics()
    return module


def printed(mod, caplog, strategy):
    caplog.clear()
    with caplog.at_level(logging.INFO):
        mod.print_stats(strategy)
    return {message.split("Stats: ")[1].split(" = ")[0]
            for message in caplog.messages if message.startswith("Stats: ") and " = " in message}


COMMON = {'F#', 'F-Initial#', 'CASE-F2-01', 'CASE-F3-01', 'CASE-F4-01',
          'TOTAL_RANDOM_KEMPE_SWITCHES', 'MAX_RANDOM_KEMPE_SWITCHES', 'time_ELABORATION'}


SHARED = ['REBUILD-', 'EXACT-', 'MEASURE-']  # S6/S7 reconstruction and perimeter measurement


@pytest.mark.parametrize("strategy,kept,dropped", [
    ('s1', ['CASE-F5-'], ['SELECT-S4-', 'S5-', 'SELECT-S5-', 'SELECT-S6-', 'S7-', 'SELECT-S7-'] + SHARED),
    ('s4', ['CASE-F5-', 'SELECT-S4-'], ['S5-', 'SELECT-S5-', 'SELECT-S6-', 'S7-', 'SELECT-S7-'] + SHARED),
    ('s5', ['CASE-F5-', 'S5-', 'SELECT-S5-'], ['SELECT-S4-', 'SELECT-S6-', 'S7-', 'SELECT-S7-'] + SHARED),
    ('s6', ['SELECT-S6-'] + SHARED, ['CASE-F5-', 'SELECT-S4-', 'S5-', 'SELECT-S5-', 'S7-', 'SELECT-S7-']),
    ('s7', ['S7-', 'SELECT-S7-'] + SHARED, ['CASE-F5-', 'SELECT-S4-', 'S5-', 'SELECT-S5-', 'SELECT-S6-']),
])
def test_only_relevant_stats_are_printed(mod, caplog, strategy, kept, dropped):
    names = printed(mod, caplog, strategy)
    assert COMMON <= names
    for prefix in kept:
        assert any(name.startswith(prefix) for name in names), prefix
    for prefix in dropped:
        assert not any(name.startswith(prefix) for name in names), prefix


def test_no_strategy_prints_everything(mod, caplog):
    assert printed(mod, caplog, None) == set(mod.stats)
