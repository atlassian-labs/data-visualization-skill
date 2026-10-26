"""Run the SKILL.md preamble and every chart-patterns.md code block on sample data.

These tests catch code that errors, invalid Plotly properties, and patterns that drift from the preamble
(palette, font, created-at annotation). They do not judge how a chart looks.

Style checks for an agent
-------------------------
Unit tests can't see layout problems, so after changing the preamble or a pattern, have an agent render each
pattern to PNG at its real size (`fig.write_image(path, width=fig.layout.width, height=fig.layout.height)`;
`pio.write_images` ignores the layout size unless you pass it) and look at every image for:

- Text collisions: the "Chart created" date overlapping axis titles or tick labels; the legend covering data,
  a secondary y-axis or its tick labels; data labels overprinting each other (e.g. a label on every scatter point);
  radar tick labels running into dimension labels.
- Axes: non-round or clipped tick labels (e.g. a secondary y-axis synced to the primary grid gives 187.89, 198.16);
  missing axis lines; gridlines drawn through bars, funnel stages or empty heatmap cells.
- Layering: reference lines and connector shapes drawn on top of markers (shapes need `layer='below'`).
- Text: literal "NaN" in heatmap cells; totals or deltas labelled with the wrong number (waterfall);
  counts shown with decimals; duplicate information (a legend repeating x-axis or slice labels).
- Colour: every colour comes from the palette or the COLOUR_* constants; the same category keeps the same colour
  across charts; the diverging scale's neutral colour sits on the meaningful midpoint (zmid);
  light palette colours (#FFB651, #DAA5AC, #61BEA4) aren't used for thin lines or text; no single-meaning
  sequence (funnel stages, histogram bins) is drawn as a rainbow.
- Overall: the chart answers its title at a glance, with no chart junk beyond the preamble's style.
"""
import json
import re

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
import pytest
from plotly.basedatatypes import BaseFigure

from conftest import Path, pattern_blocks, preamble_code

REQUIREMENTS = Path(__file__).resolve().parent / "requirements.txt"

# Plotly's default qualitative colours: none should appear in a styled chart
PLOTLY_DEFAULT_COLOURS = {c.lower() for c in plotly.colors.qualitative.Plotly}

rng = np.random.default_rng(0)


def _days(n=6):
    return pd.date_range("2024-01-01", periods=n, freq="MS")


def _series_over_time():
    days = _days()
    return pd.DataFrame({
        "day": np.tile(days.strftime("%Y-%m-%d"), 3),
        "series_col": np.repeat(["North", "South", "West"], len(days)),
        "value_col": rng.uniform(10, 100, 3 * len(days)).round(1),
    })


def _categories(n=5):
    return pd.DataFrame({
        "category_col": [f"Cat {i}" for i in range(n)],
        "value_col": rng.uniform(10, 100, n).round(1),
    })


def _hierarchy():
    # Two roots, one with children and one flat leaf, values summing up the tree (branchvalues='total')
    return pd.DataFrame({
        "id_col": ["A", "A/x", "A/y", "B"],
        "label_col": ["A", "x", "y", "B"],
        "parent_col": ["", "A", "A", ""],
        "value_col": [30, 10, 20, 15],
    })


# Variables each pattern expects to find (its placeholders), keyed by the heading above the code block.
# Every block in chart-patterns.md must have an entry, so a new pattern can't be added without a test.
SAMPLE_DATA = {
    "1. Bar Chart": lambda: {"df": _categories()},
    "2. Line Chart": lambda: {"df": _series_over_time()},
    "Event annotation (optional add-on)": lambda: {},
    "3. Scatter Plot": lambda: {"df": pd.DataFrame({
        "x_col": rng.uniform(0, 10, 50), "y_col": rng.uniform(0, 10, 50)})},
    "4. Heatmap": lambda: {"df": pd.DataFrame({
        "row_col": np.repeat(["r1", "r2", "r3"], 4),
        "col_col": np.tile(["c1", "c2", "c3", "c4"], 3),
        "value_col": rng.uniform(0, 1, 12)})},
    "5. Area Chart": lambda: {"df": _series_over_time()},
    "6. Stacked Bar Chart": lambda: {"df": pd.DataFrame({
        "category_col": np.tile(["Q1", "Q2", "Q3"], 2),
        "series_col": np.repeat(["Online", "Retail"], 3),
        "value_col": rng.uniform(10, 50, 6)})},
    "7. Bar + Line Combo": lambda: {"df": pd.DataFrame({
        "category_col": ["Jan", "Feb", "Mar", "Apr"],
        "bar_value": [120, 135, 150, 160],
        "line_value": [0.42, 0.45, 0.41, 0.48]})},
    "8. Pie Chart": lambda: {"df": _categories(4)},
    "9. Histogram": lambda: {"df": pd.DataFrame({"value_col": rng.normal(50, 10, 200)})},
    "10. Boxplot": lambda: {"df": pd.DataFrame({
        "category_col": np.repeat(["A", "B", "C"], 40), "value_col": rng.normal(50, 10, 120)})},
    "11. Bubble Chart": lambda: {"df": pd.DataFrame({
        "x_col": rng.uniform(0, 10, 20), "y_col": rng.uniform(0, 10, 20),
        "size_col": rng.uniform(1, 100, 20)})},
    "12. Violin Plot": lambda: {"df": pd.DataFrame({
        "category_col": np.repeat(["A", "B", "C"], 40), "value_col": rng.normal(50, 10, 120)})},
    "13. Funnel Chart": lambda: {"df": pd.DataFrame({
        "stage_col": ["Visit", "Sign up", "Activate", "Pay"], "value_col": [1000, 420, 210, 80]})},
    "Colour overflow": lambda: {"df": pd.DataFrame({"series_col": [f"Series {c}" for c in "ABCDEFGHI"]})},
    "14. Waterfall Chart": lambda: {"df": pd.DataFrame({
        "label_col": ["Start", "Sales", "Refunds", "End"],
        "value_col": [100, 40, -15, 0],
        "measure_col": ["absolute", "relative", "relative", "total"]})},
    "15. Sankey Diagram": lambda: {"df": pd.DataFrame({
        "source_col": ["Trial", "Trial", "Paid", "Paid"],
        "target_col": ["Paid", "Churned", "Renewed", "Cancelled"],
        "value_col": [40, 60, 30, 10]})},
    "16. Treemap": lambda: {"df": _hierarchy()},
    "17. Sunburst": lambda: {"df": _hierarchy()},
    "18. Indicator / KPI Tile": lambda: {"current_value": 1250, "previous_value": 1100},
    "KPI grid (multiple indicators)": lambda: {"metrics": [
        {"title": "Users", "value": 1250, "previous": 1100},
        {"title": "Revenue", "value": 52.3, "previous": 55.0, "format": ".1f", "suffix": "k"}]},
    "19. Horizontal Bar (Ranked)": lambda: {"df": pd.DataFrame({
        "label_col": [f"Item {i}" for i in range(8)], "value_col": rng.uniform(10, 100, 8)})},
    "20. Dumbbell Chart": lambda: {"df": pd.DataFrame({
        "label_col": ["A", "B", "C", "D"], "before_col": [10, 20, 30, 40], "after_col": [15, 18, 38, 41]})},
    "21. Radar / Spider Chart": lambda: {"df": pd.DataFrame({
        "series_col": np.repeat(["Team A", "Team B"], 5),
        "dimension_col": np.tile(["Speed", "Quality", "Cost", "Scope", "Risk"], 2),
        "value_col": rng.uniform(20, 90, 10)})},
    "22. Cohort Retention Heatmap": lambda: {"df": pd.DataFrame(
        [[100, 62.5, 48.1, 40.0], [100, 58.3, 45.2, np.nan], [100, 65.0, np.nan, np.nan]],
        index=["2024-01", "2024-02", "2024-03"], columns=[0, 1, 2, 3])},
    "Semantic colour conventions": lambda: {},
}

# Blocks that are fragments or helpers rather than a whole chart
NON_CHART_BLOCKS = {"Event annotation (optional add-on)", "Colour overflow", "Semantic colour conventions"}

BLOCKS = pattern_blocks()


@pytest.fixture(autouse=True)
def no_show(monkeypatch):
    """Patterns end with fig.show(); don't open a browser or renderer during tests."""
    monkeypatch.setattr(BaseFigure, "show", lambda self, *args, **kwargs: None)


def run_pattern(heading):
    ns = {}
    exec(preamble_code(), ns)
    ns.update(SAMPLE_DATA[heading]())
    exec(BLOCKS[heading], ns)
    return ns


def test_plotly_version_is_pinned():
    pinned = re.search(r"^plotly==(\S+)$", REQUIREMENTS.read_text(), re.M).group(1)
    assert plotly.__version__ == pinned, (
        f"Run tests with the pinned plotly {pinned} (pip install -r tests/requirements.txt), got {plotly.__version__}"
    )


def test_every_pattern_has_sample_data():
    assert set(BLOCKS) == set(SAMPLE_DATA), (
        f"Missing sample data: {sorted(set(BLOCKS) - set(SAMPLE_DATA))}; "
        f"stale entries: {sorted(set(SAMPLE_DATA) - set(BLOCKS))}"
    )


@pytest.mark.parametrize("heading", sorted(BLOCKS))
def test_pattern_does_not_redefine_preamble(heading):
    assert "def get_layout" not in BLOCKS[heading], "Patterns must use the preamble, not re-embed it"


@pytest.mark.parametrize("heading", sorted(BLOCKS))
def test_pattern_runs(heading):
    run_pattern(heading)


@pytest.mark.parametrize("heading", sorted(set(BLOCKS) - NON_CHART_BLOCKS))
def test_pattern_follows_preamble_style(heading):
    ns = run_pattern(heading)
    fig = ns["fig"]

    assert isinstance(fig, go.Figure) and len(fig.data) >= 1
    assert fig.layout.font.family == ns["FONT_FAMILY"], "Layout must come from get_layout()"
    assert list(fig.layout.colorway) == ns["chart_colours"]
    assert any((a.text or "").startswith("Chart created:") for a in fig.layout.annotations), (
        "Call add_created_at_annotation(fig) before fig.show()"
    )

    # Skip layout.template: Plotly's built-in template always lists its default palette
    fig_dict = json.loads(fig.to_json())
    fig_dict["layout"].pop("template", None)
    fig_json = json.dumps(fig_dict).lower()
    leaked = {c for c in PLOTLY_DEFAULT_COLOURS if c in fig_json}
    assert not leaked, f"Plotly default colours leaked into the chart: {sorted(leaked)}"


def test_event_annotation_helper():
    ns = run_pattern("Event annotation (optional add-on)")
    fig = ns["go"].Figure(layout=ns["get_layout"]())
    ns["annotate_event"](fig, x="2024-03-01", ymin=0, ymax=10, text_x="2024-03-15", text="Launch")
    assert len(fig.layout.shapes) == 1 and fig.layout.annotations[0].text == "Launch"


# Regression tests for bugs found by rendering the patterns on real data

def test_waterfall_labels_totals_with_computed_value():
    # A 'total' passed as 0 must not be labelled with the raw y (formatted %{y} prints the input)
    fig = run_pattern("14. Waterfall Chart")["fig"]
    trace = fig.data[0]
    for measure, template in zip(trace.measure, trace.texttemplate):
        expected = "%{delta" if measure == "relative" else "%{final"
        assert template.startswith(expected), f"{measure} bar labelled with {template!r}"
    assert "%{y" not in trace.hovertemplate


def test_scatter_does_not_label_every_point():
    fig = run_pattern("3. Scatter Plot")["fig"]
    assert "text" not in fig.data[0].mode


def test_heatmap_documents_zmid_for_diverging_scale():
    assert re.search(r"zmid", BLOCKS["4. Heatmap"]), "Heatmap pattern must show zmid for DIVERGING_SCALE"


# Preamble behaviour

def test_get_layout_overrides_merge_with_defaults(preamble_ns):
    layout = preamble_ns["get_layout"](title=dict(text="Title"), xaxis_title="X")
    assert layout.title.text == "Title"
    assert layout.title.font.size == preamble_ns["TITLE_SIZE"], "Override replaced nested title defaults"
    assert layout.title.x == 0.5
    assert layout.xaxis.title.text == "X"
    assert layout.xaxis.showline is True, "Override replaced nested xaxis defaults"


def test_series_colours_cycles(preamble_ns):
    palette = preamble_ns["chart_colours"]
    colours = preamble_ns["series_colours"](len(palette) + 2)
    assert colours[:len(palette)] == palette
    assert colours[len(palette):] == palette[:2]


def test_hex_to_rgba(preamble_ns):
    assert preamble_ns["hex_to_rgba"]("#2E92A2", 0.3) == "rgba(46, 146, 162, 0.3)"


def test_created_at_annotation_keeps_larger_bottom_margin(preamble_ns):
    go_ = preamble_ns["go"]
    small = go_.Figure(layout=preamble_ns["get_layout"]())
    preamble_ns["add_created_at_annotation"](small)
    assert small.layout.margin.b == 100

    large = go_.Figure(layout=preamble_ns["get_layout"](margin=dict(b=160)))
    preamble_ns["add_created_at_annotation"](large)
    assert large.layout.margin.b == 160


def test_preamble_json_serialisable(preamble_ns):
    json.loads(preamble_ns["go"].Figure(layout=preamble_ns["get_layout"]()).to_json())
