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


def test_v2_exposes_accessible_shell_controls():
    source = V2.read_text(encoding="utf-8")
    parser = IdParser()
    parser.feed(source)
    v2_ids = {
        "btnOpenSettings", "btnCloseSettings", "settingsDrawer",
        "settingsBackdrop", "graphStats", "actionStatus",
    }
    assert v2_ids <= set(parser.ids)
    assert parser.attributes_by_id["btnOpenSettings"]["aria-controls"] == "settingsDrawer"
    assert parser.attributes_by_id["actionStatus"]["aria-live"] == "polite"


def test_v2_ui_helpers_change_observable_dom_state(tmp_path):
    source = V2.read_text(encoding="utf-8")
    match = re.search(r'<script id="ui-layer">(.*?)</script>', source, re.S)
    assert match, "ui-layer script must be executable in isolation"
    harness = """
const elements = new Map();
function element() {
  return { hidden: true, textContent: '', dataset: {}, attrs: {},
    classList: { values: new Set(), toggle(name, on) { on ? this.values.add(name) : this.values.delete(name); } },
    setAttribute(name, value) { this.attrs[name] = value; } };
}
['settingsDrawer','settingsBackdrop','btnOpenSettings','graphStats','actionStatus'].forEach(id => elements.set(id, element()));
global.document = { getElementById: id => elements.get(id) || null };
global.state = { graph: { order: 4, size: 6 } };
""" + match.group(1) + """
setSettingsOpen(true);
updateGraphStats();
setActionStatus('Completata', 'success');
console.log(JSON.stringify({
  open: elements.get('settingsDrawer').classList.values.has('is-open'),
  expanded: elements.get('btnOpenSettings').attrs['aria-expanded'],
  backdropHidden: elements.get('settingsBackdrop').hidden,
  stats: elements.get('graphStats').textContent,
  status: elements.get('actionStatus').textContent,
  tone: elements.get('actionStatus').dataset.tone
}));
"""
    script = tmp_path / "ui-layer-test.js"
    script.write_text(harness, encoding="utf-8")
    completed = subprocess.run(["node", script], text=True, capture_output=True, check=True)
    assert json.loads(completed.stdout) == {
        "open": True, "expanded": "true", "backdropHidden": False,
        "stats": "4 nodi · 6 archi", "status": "Completata", "tone": "success",
    }
