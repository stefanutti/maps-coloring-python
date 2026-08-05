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
    "cfgNodeWidth", "cfgNodeLabelFontSize", "cfgEdgeLabelFontSize",
    "cfgPhysicsSpringLength", "cfgPhysicsRepulsion",
    "cfgPhysicsSpringStrength", "cfgPhysicsDamping",
    "cfgPhysicsMaxVelocity", "cfgNodeColor", "cfgEdgeColor",
}


class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.script_sources = []
        self.attributes_by_id = {}
        self.ancestor_ids_by_id = {}
        self.text_by_id = {}
        self._stack = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
            self.attributes_by_id[attributes["id"]] = attributes
            self.ancestor_ids_by_id[attributes["id"]] = tuple(
                ancestor_attrs["id"]
                for _, ancestor_attrs in self._stack
                if "id" in ancestor_attrs
            )
            self.text_by_id[attributes["id"]] = []
        if tag == "script" and "src" in attributes:
            self.script_sources.append(attributes["src"])
        self._stack.append((tag, attributes))

    def handle_endtag(self, tag):
        matching_index = next(
            (index for index in range(len(self._stack) - 1, -1, -1)
             if self._stack[index][0] == tag),
            None,
        )
        if matching_index is not None:
            del self._stack[matching_index:]

    def handle_data(self, data):
        for _, attributes in self._stack:
            element_id = attributes.get("id")
            if element_id:
                self.text_by_id[element_id].append(data)

    def text(self, element_id):
        return " ".join("".join(self.text_by_id[element_id]).split())


def inline_script(source, script_id):
    match = re.search(
        rf'<script id="{re.escape(script_id)}">(.*?)</script>', source, re.S
    )
    assert match, f"{script_id} script must be executable in isolation"
    return match.group(1)


def run_node_harness(tmp_path, name, javascript):
    script = tmp_path / name
    script.write_text(javascript, encoding="utf-8")
    completed = subprocess.run(
        ["node", script], text=True, capture_output=True, check=True
    )
    return json.loads(completed.stdout)


def javascript_function(source, name, following_name):
    marker = f"    function {name}("
    start = source.index(marker)
    end = source.index(f"\n    function {following_name}(", start)
    return source[start:end]


def css_declarations(source, selector):
    style = re.search(r"<style>(.*?)</style>", source, re.S)
    assert style, "page must include its visual design"
    matches = re.findall(
        rf"(?:^|\}})\s*{re.escape(selector)}\s*\{{([^{{}}]*)\}}",
        style.group(1),
        re.S,
    )
    declarations = {}
    for body in matches[:1]:
        for declaration in body.split(";"):
            if ":" in declaration:
                property_name, value = declaration.split(":", 1)
                declarations[property_name.strip()] = value.strip()
    return declarations


def css_declarations_in_media(source, media_query, selector):
    match = re.search(
        rf"@media\s*\({re.escape(media_query)}\)\s*\{{.*?"
        rf"{re.escape(selector)}\s*\{{([^{{}}]*)\}}",
        source,
        re.S,
    )
    assert match, f"{selector} must be defined inside @media ({media_query})"
    declarations = {}
    for declaration in match.group(1).split(";"):
        if ":" in declaration:
            property_name, value = declaration.split(":", 1)
            declarations[property_name.strip()] = value.strip()
    return declarations


def resolve_css_color(source, value):
    variable_match = re.fullmatch(r"var\((--[\w-]+)\)", value)
    if not variable_match:
        return value
    root = css_declarations(source, ":root")
    return root[variable_match.group(1)]


def contrast_ratio(foreground, background):
    def luminance(hex_color):
        if re.fullmatch(r"#[0-9a-fA-F]{3}", hex_color):
            hex_color = "#" + "".join(channel * 2 for channel in hex_color[1:])
        channels = [int(hex_color[index:index + 2], 16) / 255
                    for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045
                  else ((channel + 0.055) / 1.055) ** 2.4
                  for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted(
        (luminance(foreground), luminance(background)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


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
    assert "inert" in parser.attributes_by_id["settingsDrawer"]


def test_v2_ui_helpers_change_observable_dom_state(tmp_path):
    source = V2.read_text(encoding="utf-8")
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
""" + inline_script(source, "ui-layer") + """
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


def test_graph_labels_have_readable_contrast_and_size(tmp_path):
    source = V2.read_text(encoding="utf-8")
    initializer = javascript_function(
        source, "initializeCytoscapeRenderer", "applyLabelVisibility"
    )
    harness = """
let capturedOptions = null;
const state = { cy: null };
const config = {
  nodeBaseSize: 5, edgeBaseWidth: 1,
  nodeLabelFontSize: 11, edgeLabelFontSize: 9
};
const container = {};
function debug() {}
function buildCytoscapeElements() { return []; }
function setupCytoscapeInteractions() {}
function applyLabelVisibility() {}
function applyNodeBaseSize() {}
function applyEdgeBaseWidth() {}
function applyNodeLabelFontSize() {}
function applyEdgeLabelFontSize() {}
function syncSplitEdgeSelectionToCy() {}
function cytoscape(options) {
  capturedOptions = options;
  return {
    destroy() {},
    nodes() { return { length: 0 }; },
    edges() { return { length: 0 }; },
    elements() { return {}; },
    fit() {}
  };
}
""" + initializer + """
initializeCytoscapeRenderer();
const styles = Object.fromEntries(
  capturedOptions.style.map(entry => [entry.selector, entry.style])
);
console.log(JSON.stringify({ node: styles.node, edge: styles.edge }));
"""
    styles = run_node_harness(tmp_path, "graph-label-styles.js", harness)
    node_style = styles["node"]
    edge_style = styles["edge"]

    assert contrast_ratio(
        node_style["color"], node_style["text-background-color"]
    ) >= 4.5
    assert 10 <= node_style["font-size"] <= 11
    assert node_style["text-background-opacity"] >= 0.85
    assert contrast_ratio(edge_style["color"], edge_style["text-outline-color"]) >= 4.5
    assert 8 <= edge_style["font-size"] <= 9
    assert edge_style["text-outline-width"] >= 2


def test_v2_bootstrap_reports_missing_dependencies_and_startup_errors(tmp_path):
    source = V2.read_text(encoding="utf-8")
    harness = """
const listeners = {};
const status = { textContent: '', dataset: {} };
const actions = [{ disabled: false }, { disabled: false }, { disabled: false }];
global.document = {
  getElementById(id) { return id === 'actionStatus' ? status : null; },
  querySelectorAll() { return actions; }
};
global.window = {
  addEventListener(name, listener) { listeners[name] = listener; }
};
""" + inline_script(source, "bootstrap-layer") + """
let initializationCalls = 0;
const missingResult = startGraphApplication(() => { initializationCalls += 1; }, window);
const missing = {
  result: missingResult,
  initializationCalls,
  status: status.textContent,
  tone: status.dataset.tone,
  disabled: actions.every(action => action.disabled)
};
window.graphology = { MultiUndirectedGraph: function MultiUndirectedGraph() {} };
window.cytoscape = () => {};
const exceptionResult = startGraphApplication(() => {
  initializationCalls += 1;
  throw new Error('renderer non disponibile');
}, window);
const exception = {
  result: exceptionResult,
  initializationCalls,
  status: status.textContent,
  tone: status.dataset.tone,
  disabled: actions.every(action => action.disabled)
};
listeners.error({ message: 'errore globale' });
const diagnostic = {
  status: status.textContent,
  tone: status.dataset.tone,
  disabled: actions.every(action => action.disabled)
};
console.log(JSON.stringify({ missing, exception, diagnostic }));
"""
    assert run_node_harness(tmp_path, "bootstrap-test.js", harness) == {
        "missing": {
            "result": False,
            "initializationCalls": 0,
            "status": (
                "Impossibile inizializzare il grafo: dipendenze non disponibili "
                "(Graphology, Cytoscape). Controlla la connessione e ricarica la pagina."
            ),
            "tone": "error",
            "disabled": True,
        },
        "exception": {
            "result": False,
            "initializationCalls": 1,
            "status": "Impossibile inizializzare il grafo: renderer non disponibile",
            "tone": "error",
            "disabled": True,
        },
        "diagnostic": {
            "status": "Errore imprevisto: errore globale",
            "tone": "error",
            "disabled": True,
        },
    }


def test_v2_drawer_contains_focus_and_restores_trigger(tmp_path):
    source = V2.read_text(encoding="utf-8")
    harness = """
const listeners = {};
const elements = new Map();
global.document = { activeElement: null, getElementById: id => elements.get(id) || null };
function element(id) {
  return {
    id, hidden: false, disabled: false, tabIndex: 0, inert: false, attrs: {},
    classList: { values: new Set(), toggle(name, on) { on ? this.values.add(name) : this.values.delete(name); } },
    setAttribute(name, value) { this.attrs[name] = value; },
    getAttribute(name) { return this.attrs[name]; },
    toggleAttribute(name, on) { on ? this.attrs[name] = '' : delete this.attrs[name]; },
    focus() { document.activeElement = this; }
  };
}
['settingsDrawer','settingsBackdrop','btnOpenSettings','btnCloseSettings','drawerField','drawerReset'].forEach(id => elements.set(id, element(id)));
const drawer = elements.get('settingsDrawer');
const close = elements.get('btnCloseSettings');
const field = elements.get('drawerField');
const reset = elements.get('drawerReset');
drawer.querySelectorAll = () => [close, field, reset];
let pendingAnimationFrame = null;
global.window = {
  addEventListener(name, listener) { listeners[name] = listener; },
  requestAnimationFrame(callback) { pendingAnimationFrame = callback; }
};
global.state = { graph: null };
""" + inline_script(source, "ui-layer") + """
initializeSettingsDrawer();
elements.get('btnOpenSettings').onclick();
elements.get('btnOpenSettings').focus();
if (pendingAnimationFrame) pendingAnimationFrame();
const opened = {
  inert: drawer.inert,
  ariaHidden: drawer.attrs['aria-hidden'],
  focused: document.activeElement.id,
  backdropHidden: elements.get('settingsBackdrop').hidden
};
document.activeElement = reset;
let tabPrevented = false;
listeners.keydown({ key: 'Tab', shiftKey: false, preventDefault() { tabPrevented = true; } });
const wrappedFocus = { focused: document.activeElement.id, prevented: tabPrevented };
let escapePrevented = false;
listeners.keydown({ key: 'Escape', preventDefault() { escapePrevented = true; } });
const escaped = {
  inert: drawer.inert,
  ariaHidden: drawer.attrs['aria-hidden'],
  focused: document.activeElement.id,
  backdropHidden: elements.get('settingsBackdrop').hidden,
  prevented: escapePrevented
};
elements.get('btnOpenSettings').onclick();
elements.get('btnCloseSettings').onclick();
const buttonFocused = document.activeElement.id;
elements.get('btnOpenSettings').onclick();
elements.get('settingsBackdrop').onclick();
console.log(JSON.stringify({
  opened, wrappedFocus, escaped, buttonFocused,
  backdropFocused: document.activeElement.id
}));
"""
    assert run_node_harness(tmp_path, "drawer-test.js", harness) == {
        "opened": {
            "inert": False,
            "ariaHidden": "false",
            "focused": "btnCloseSettings",
            "backdropHidden": False,
        },
        "wrappedFocus": {"focused": "btnCloseSettings", "prevented": True},
        "escaped": {
            "inert": True,
            "ariaHidden": "true",
            "focused": "btnOpenSettings",
            "backdropHidden": True,
            "prevented": True,
        },
        "buttonFocused": "btnOpenSettings",
        "backdropFocused": "btnOpenSettings",
    }


def test_v2_places_secondary_controls_in_dock_and_groups_parameters():
    parser = IdParser()
    parser.feed(V2.read_text(encoding="utf-8"))
    dock_controls = {
        "toggleNodeLabels", "toggleEdgeLabels", "toggleDebug",
        "btnExportDot", "btnOpenSettings",
    }
    assert all("toolDock" in parser.ancestor_ids_by_id[control]
               for control in dock_controls)
    assert "group-transform" in parser.ancestor_ids_by_id["btnSplitEdges"]
    assert "group-transform" not in parser.ancestor_ids_by_id["btnExportDot"]
    appearance_controls = {
        "cfgEdgeWidth", "cfgNodeWidth", "cfgNodeLabelFontSize",
        "cfgEdgeLabelFontSize", "cfgNodeColor", "cfgEdgeColor",
    }
    physics_controls = {
        "cfgPhysicsSpringLength", "cfgPhysicsRepulsion",
        "cfgPhysicsSpringStrength", "cfgPhysicsDamping",
        "cfgPhysicsMaxVelocity",
    }
    assert all("group-appearance" in parser.ancestor_ids_by_id[control]
               for control in appearance_controls)
    assert all("group-physics" in parser.ancestor_ids_by_id[control]
               for control in physics_controls)
    assert parser.attributes_by_id["cfgNodeLabelFontSize"]["value"] == "11"
    assert parser.attributes_by_id["cfgNodeLabelFontSize"]["min"] == "8"
    assert parser.attributes_by_id["cfgEdgeLabelFontSize"]["value"] == "9"
    assert parser.attributes_by_id["cfgEdgeLabelFontSize"]["min"] == "7"
    assert parser.text("appearanceTitle") == "Aspetto"
    assert parser.text("physicsTitle") == "Fisica"
    assert parser.text("appTitle") == "4CT Split & Bridge"


def test_label_font_size_controls_update_and_reset_config_and_renderer(tmp_path):
    source = V2.read_text(encoding="utf-8")
    config_state = source[
        source.index("    const DEFAULT_CONFIG"):
        source.index("    function createApplicationState")
    ]
    node_label_size = javascript_function(
        source, "applyNodeLabelFontSize", "applyEdgeLabelFontSize"
    )
    edge_label_start = source.index("    function applyEdgeLabelFontSize(")
    edge_label_end = source.index("\n    const CONFIG_CONTROL_DEFS", edge_label_start)
    edge_label_size = source[edge_label_start:edge_label_end]
    config_controls_start = source.index("    const CONFIG_CONTROL_DEFS")
    config_controls_end = source.index("\n    function setupConfigControls", config_controls_start)
    config_controls = source[config_controls_start:config_controls_end]
    harness = """
const elements = new Map([
  ['cfgNodeLabelFontSize', { value: '' }],
  ['cfgEdgeLabelFontSize', { value: '' }]
]);
global.document = { getElementById: id => elements.get(id) || null };
const styleValues = {};
const styleUpdates = [];
const styleApi = {
  selector(name) { this.selectorName = name; return this; },
  style(name, value) { styleValues[this.selectorName] = value; return this; },
  update() { styleUpdates.push(this.selectorName); return this; }
};
const state = { cy: { style() { return styleApi; } } };
""" + config_state + node_label_size + edge_label_size + config_controls + """
const nodeDef = CONFIG_CONTROL_DEFS.find(def => def.id === 'cfgNodeLabelFontSize');
const edgeDef = CONFIG_CONTROL_DEFS.find(def => def.id === 'cfgEdgeLabelFontSize');
applyConfigChange(nodeDef, '14');
applyConfigChange(edgeDef, '12');
const updated = {
  nodeConfig: config.nodeLabelFontSize,
  edgeConfig: config.edgeLabelFontSize,
  nodeStyle: styleValues.node,
  edgeStyle: styleValues.edge
};
resetConfigControl(nodeDef);
resetConfigControl(edgeDef);
console.log(JSON.stringify({
  updated,
  reset: {
    nodeConfig: config.nodeLabelFontSize,
    edgeConfig: config.edgeLabelFontSize,
    nodeInput: elements.get('cfgNodeLabelFontSize').value,
    edgeInput: elements.get('cfgEdgeLabelFontSize').value,
    nodeStyle: styleValues.node,
    edgeStyle: styleValues.edge
  },
  styleUpdates: styleUpdates
}));
"""
    result = run_node_harness(tmp_path, "label-font-size-controls.js", harness)
    assert result == {
        "updated": {
            "nodeConfig": 14,
            "edgeConfig": 12,
            "nodeStyle": 14,
            "edgeStyle": 12,
        },
        "reset": {
            "nodeConfig": 11,
            "edgeConfig": 9,
            "nodeInput": "11",
            "edgeInput": "9",
            "nodeStyle": 11,
            "edgeStyle": 9,
        },
        "styleUpdates": ["node", "edge", "node", "edge"],
    }


def test_v2_successful_command_clears_selection_input_and_prevents_reuse(tmp_path):
    source = V2.read_text(encoding="utf-8")
    function_source = javascript_function(
        source, "splitAndBridgeEdges", "exportToDot"
    )
    harness = """
const elements = new Map([
  ['edgeSplitInput', { value: '0, 1' }],
  ['selectionStatus', { textContent: '' }],
  ['actionStatus', { textContent: '', dataset: {} }]
]);
global.document = { getElementById: id => elements.get(id) || null };
global.window = { addEventListener() {} };
global.state = { selectedSplitEdges: ['e0', 'e1'], graph: {} };
global.debug = () => {};
""" + inline_script(source, "ui-layer") + """
function findEdgeKeyFromUserToken(token) { return { '0': 'e0', '1': 'e1' }[token] || null; }
let splitIndex = 0;
function splitEdge() { return { midNode: `n${splitIndex++}`, newEdges: [] }; }
function countEdgesBetween() { return 0; }
function addEdgeAuto() { return 'created'; }
function updateParallelEdgeGeometry() {}
function syncSplitEdgeSelectionToCy() { updateSplitSelectionUi(state.selectedSplitEdges); }
function syncGraphToCytoscape() {}
function ensurePhysicsVelocities() {}
function startPhysics() {}
""" + function_source + """
const first = handleSplitAndBridgeCommand();
const afterFirst = {
  ok: first.ok,
  selected: state.selectedSplitEdges,
  input: elements.get('edgeSplitInput').value,
  selectionStatus: elements.get('selectionStatus').textContent,
  actionStatus: elements.get('actionStatus').textContent,
  tone: elements.get('actionStatus').dataset.tone
};
const second = handleSplitAndBridgeCommand();
console.log(JSON.stringify({
  afterFirst,
  afterSecond: {
    ok: second.ok,
    input: elements.get('edgeSplitInput').value,
    actionStatus: elements.get('actionStatus').textContent,
    tone: elements.get('actionStatus').dataset.tone
  }
}));
"""
    assert run_node_harness(tmp_path, "selection-reset-test.js", harness) == {
        "afterFirst": {
            "ok": True,
            "selected": [],
            "input": "",
            "selectionStatus": "0 di 2 archi selezionati",
            "actionStatus": "Trasformazione completata.",
            "tone": "success",
        },
        "afterSecond": {
            "ok": False,
            "input": "",
            "actionStatus": "Inserisci esattamente due ID separati da una virgola.",
            "tone": "error",
        },
    }


def test_v2_transform_failures_emit_detailed_debug_messages(tmp_path):
    source = V2.read_text(encoding="utf-8")
    function_source = javascript_function(
        source, "splitAndBridgeEdges", "exportToDot"
    )
    harness = """
const state = { graph: {} };
let edgeKeys = {};
let splitResults = [];
let logs = [];
function debug(tag, message = '') { logs.push({ tag, message }); }
function findEdgeKeyFromUserToken(token) { return edgeKeys[token] || null; }
function splitEdge() { return splitResults.shift() || null; }
function countEdgesBetween() { return 0; }
function addEdgeAuto() { return 'created'; }
function updateParallelEdgeGeometry() {}
function syncGraphToCytoscape() {}
function ensurePhysicsVelocities() {}
function startPhysics() {}
""" + function_source + """
function run(tokens, keys, splits) {
  edgeKeys = keys;
  splitResults = splits.slice();
  logs = [];
  const result = splitAndBridgeEdges(tokens[0], tokens[1]);
  const info = logs.filter(entry => entry.tag === 'info').map(entry => entry.message);
  return { result, info };
}
console.log(JSON.stringify([
  run(['missing-a', '1'], {}, []),
  run(['0', 'missing-b'], { '0': 'e0' }, []),
  run(['0', '0'], { '0': 'e0' }, [null]),
  run(['0', '0'], { '0': 'e0' }, [{ midNode: 'n0', newEdges: ['e2'] }, null]),
  run(['0', '1'], { '0': 'e0', '1': 'e1' }, [null]),
  run(['0', '1'], { '0': 'e0', '1': 'e1' }, [{ midNode: 'n0' }, null])
]));
"""
    failures = run_node_harness(tmp_path, "transform-failures-test.js", harness)
    assert [failure["info"][-1:] for failure in failures] == [
        ['Arco "missing-a" non trovato.'],
        ['Arco "missing-b" non trovato.'],
        ["Split fallito per l’arco e0."],
        ["Secondo split fallito per l’arco e2."],
        ["Split della prima edge e0 fallito."],
        ["Split della seconda edge e1 fallito."],
    ]
    assert all(failure["result"] == {
        "ok": False,
        "message": ('Arco "missing-a" non trovato.'
                    if index == 0 else 'Arco "missing-b" non trovato.'
                    if index == 1 else "Impossibile dividere l’arco selezionato."),
    } for index, failure in enumerate(failures))


def test_v2_visual_contract_has_contrast_texture_and_responsive_dock():
    source = V2.read_text(encoding="utf-8")
    success = css_declarations(source, '.action-status[data-tone="success"]')
    error = css_declarations(source, '.action-status[data-tone="error"]')
    background = resolve_css_color(source, "var(--panel-fallback)")
    assert contrast_ratio(resolve_css_color(source, success["color"]), background) >= 4.5
    assert contrast_ratio(resolve_css_color(source, error["color"]), background) >= 4.5
    graph_container = css_declarations(source, "#graph-container")
    assert "radial-gradient" in graph_container["background-image"]
    command_card = css_declarations(source, ".command-card")
    assert command_card["top"] == "1rem"
    assert command_card["left"] == "1rem"
    assert command_card["right"] == "auto"
    responsive_command_card = css_declarations_in_media(
        source, "max-width: 760px", ".command-card"
    )
    assert responsive_command_card["top"] == "1rem"
    assert responsive_command_card["left"] == "1rem"
    assert responsive_command_card["right"] == "auto"
    tool_dock = css_declarations(source, ".tool-dock")
    assert tool_dock["flex-wrap"] == "wrap"
