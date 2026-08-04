from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess

CT_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = CT_ROOT / "web_split_and_bridge/split_and_bridge.html"
V2 = CT_ROOT / "web_split_and_bridge/split_and_bridge_v2.html"

REQUIRED_IDS = {
    "graph-container", "edgeSplitInput", "btnSplitEdges", "btnExportDot",
    "toggleNodeLabels", "toggleEdgeLabels", "toggleDebug", "cfgEdgeWidth",
    "cfgNodeWidth", "cfgPhysicsSpringLength", "cfgPhysicsRepulsion",
    "cfgPhysicsSpringStrength", "cfgPhysicsDamping",
    "cfgPhysicsMaxVelocity", "cfgNodeColor", "cfgEdgeColor",
}


class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.script_sources = []
        self.attributes_by_id = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
            self.attributes_by_id[attributes["id"]] = attributes
        if tag == "script" and "src" in attributes:
            self.script_sources.append(attributes["src"])


def test_v2_has_unique_required_control_ids():
    parser = IdParser()
    parser.feed(V2.read_text(encoding="utf-8"))
    assert REQUIRED_IDS <= set(parser.ids)
    assert len(parser.ids) == len(set(parser.ids))


def test_v2_preserves_runtime_dependencies():
    parser = IdParser()
    parser.feed(V2.read_text(encoding="utf-8"))
    assert parser.script_sources == [
        "https://unpkg.com/graphology@0.25.4/dist/graphology.umd.min.js",
        "https://unpkg.com/cytoscape@3.27.0/dist/cytoscape.min.js",
    ]


def test_original_page_remains_tracked_as_a_separate_file():
    assert ORIGINAL.exists()
    assert V2.resolve() != ORIGINAL.resolve()
