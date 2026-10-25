---
name: visualization
description: "Data visualization using Plotly with Atlassian's internal design principles. Generates clean, publication-quality charts with a consistent colour palette, a single editable style preamble, and a creation date annotation. Use when: charts, plots, visualizations, graphs, bar chart, line chart, scatter plot, heatmap, area chart, pie chart, histogram, boxplot, bubble chart, violin plot, funnel chart, waterfall, Sankey, treemap, Plotly, or styling an existing chart."
labels:
  - analytics
  - charts
  - visualization
metadata:
  version: 0.1.0
---

# Visualization Standard

Plotly charts that maximise data and minimise decoration: light grids, no chart junk, direct labels, one consistent palette.

## When to use

- Creating any data visualization from a DataFrame
- Building publication-quality Plotly charts with a consistent style
- Choosing the right chart type for a dataset
- Restyling an existing Plotly chart to match this standard

## Workflow

### 1. Preamble code (required, once per notebook or script)

Include the preamble **once**, near the top, after imports and before any chart code. Do NOT repeat or re-embed it in chart cells. Chart cells should only contain data prep and the `go.Figure(...)` call.

If a cell or file containing `def get_layout` already exists, skip this step.

Everything a user is likely to want to change (palette, fonts, sizes, colours) sits in the block marked `STYLE SETTINGS`. Edit that block to restyle every chart. Do not edit the functions below it.

```python
import plotly.graph_objects as go
from datetime import datetime

# =============================================================================
# STYLE SETTINGS: edit this block to restyle every chart
# =============================================================================

# Palette: "Lupi" from the MoMAColors R package (MIT), https://github.com/BlakeRMills/MoMAColors
chart_colours = ['#2E92A2', '#FFB651', '#AA3F5D', '#98A54F', '#D85A44', '#61BEA4', '#DAA5AC']

# Semantic colours: use when colour carries meaning (gain/loss, target, etc.)
COLOUR_POSITIVE = '#2E92A2'
COLOUR_NEGATIVE = '#D85A44'
COLOUR_TOTAL = '#444444'
COLOUR_WARNING = '#FFB651'
COLOUR_HIGHLIGHT = '#AA3F5D'
COLOUR_MUTED = '#A0A0A0'      # de-emphasised series, connectors, reference lines

# Text, grid and background
COLOUR_TEXT = '#222222'
COLOUR_GRID = 'lightgray'
COLOUR_BACKGROUND = 'white'
FONT_FAMILY = "Helvetica Neue, Helvetica, Arial, sans-serif"

# Continuous colour scales (heatmaps)
SEQUENTIAL_SCALE = [[0.0, '#E9F7F4'], [0.5, '#61BEA4'], [1.0, '#1B5E6B']]
DIVERGING_SCALE = [[0.0, '#D85A44'], [0.5, '#F7F7F7'], [1.0, '#2E92A2']]

# Default chart size (pixels) and font sizes
CHART_WIDTH = 700
CHART_HEIGHT = 400
TITLE_SIZE = 24
BODY_SIZE = 14

# =============================================================================
# Helpers: do not edit below this line
# =============================================================================

def series_colours(n):
    """Return n colours from chart_colours, cycling if n exceeds the palette length."""
    return [chart_colours[i % len(chart_colours)] for i in range(n)]

def hex_to_rgba(hex_colour, alpha):
    """Convert '#RRGGBB' to an 'rgba(r, g, b, alpha)' string for translucent fills."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"

def get_layout(**kwargs):
    """Return a styled Plotly layout. Pass any go.Layout kwargs to override defaults."""
    defaults = dict(
        colorway=chart_colours,
        autosize=False,
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        font=dict(family=FONT_FAMILY, size=BODY_SIZE, color=COLOUR_TEXT),
        title=dict(x=0.5, font={"size": TITLE_SIZE}),
        xaxis=dict(
            showgrid=False,
            gridcolor=COLOUR_GRID,
            showline=True,
            linecolor='black',
            automargin=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLOUR_GRID,
            showline=True,
            linecolor='black',
            automargin=True,
        ),
        legend=dict(x=1, y=1, bgcolor="rgba(255, 255, 255, 0.95)"),
        margin=dict(l=50, r=50, b=50, t=50, pad=1),
        showlegend=True,
        paper_bgcolor=COLOUR_BACKGROUND,
        plot_bgcolor=COLOUR_BACKGROUND,
        hoverlabel=dict(
            font=dict(family=FONT_FAMILY, size=12, color=COLOUR_TEXT),
            bgcolor="white",
            bordercolor=COLOUR_TEXT,
        ),
    )
    layout = go.Layout(**defaults)
    layout.update(**kwargs)
    return layout

def add_created_at_annotation(fig, *, offset_px=65, bottom_margin_px=100):
    """Add a 'Chart created: YYYY-MM-DD' annotation to the bottom-right of the chart. Adjust spacing for dense labels."""
    chart_created_at_str = datetime.now().strftime("%Y-%m-%d")
    fig.update_layout(margin=dict(b=max(fig.layout.margin.b or 0, bottom_margin_px)))
    fig.add_annotation(
        text=f"Chart created: {chart_created_at_str}",
        xref="paper", yref="paper",
        x=1, y=0,
        yshift=-offset_px,
        xanchor="right", yanchor="top",
        showarrow=False,
        font=dict(size=12),
    )
```

> **Anti-pattern: never do this:**
>
> ```python
> # WRONG: bare layout variable, no override support
> layout = go.Layout(...)
> fig = go.Figure(layout=layout)
>
> # CORRECT: always use get_layout() and add_created_at_annotation()
> fig = go.Figure(data=[...], layout=get_layout(title=dict(text="My Chart", x=0.5, font={"size": 24})))
> add_created_at_annotation(fig)
> ```

### 2. Generate chart code

- Assume the user already has their DataFrame unless they ask you to load data.
- Always use `chart_colours` (or `series_colours(n)`) and the `COLOUR_*` constants. Never let Plotly's default colours through.
- See [chart-patterns.md](./references/chart-patterns.md) for complete, ready-to-use code for every chart type.

### 3. Chart selection guidance

If the user needs help choosing a chart type:

| Data pattern | Primary choice | Alternative | When to avoid |
|---|---|---|---|
| Compare categories | Bar | Horizontal bar (>8 cats), Lollipop | >20 categories without grouping |
| Trend over time | Line | Area (cumulative), Sparkline (compact) | Fewer than 3 time points |
| Part of whole | Stacked Bar | Pie (≤5 cats), Treemap (hierarchical) | >5 slices in pie |
| Distribution | Histogram | Boxplot (multi-group), Violin (shape) | Small samples (<30) |
| Correlation | Scatter | Bubble (add 3rd variable) | Categorical-only data |
| Matrix / cross-tab | Heatmap | n/a | Very sparse matrices |
| Incremental changes | Waterfall | Stacked bar | Many categories (>10 steps) |
| Flow / migration | Sankey | Parallel categories | >6 source/target nodes |
| Hierarchy | Treemap | Sunburst (deeper nesting) | Flat (non-hierarchical) data |
| Ranked list | Horizontal Bar | Lollipop / Dot plot | Fewer than 5 items |
| Before → after | Dumbbell | Grouped bar | More than 2 time points (use line) |
| Single KPI | Indicator | Bullet chart (vs target) | Need to show distribution |
| Multi-dimensional | Radar | Parallel categories | >8 dimensions (unreadable) |
| Stage progression | Funnel | Horizontal bar | Non-sequential stages |
| Cohort × period matrix | Heatmap | n/a | Fewer than 3 cohorts |

Further reading on choosing and building each chart type: https://www.atlassian.com/data/charts

## Modes of operation

### Quick mode (default)
User provides all required details. Generate code immediately. Fill gaps with reasonable assumptions and state them.

### Interactive mode
Guide the user step by step to gather all chart inputs, then confirm the plan before generating code.

## Required chart inputs

For each visualization, ensure you have (or make reasonable assumptions for):

| Input | Description | Example |
|-------|-------------|---------|
| Chart type | bar, line, area, scatter, heatmap, histogram, boxplot, pie, bubble, violin, funnel | `bar` |
| Input data | DataFrame structure with column names | `df with columns: day, region, avg_sales` |
| x-axis | Column for x-axis | `region` |
| y-axis | Column for y-axis | `avg_sales` |
| x-axis label | Display label | `"Region"` |
| y-axis label | Display label | `"Average sales"` |
| Chart title | Title text | `"Average sales by region"` |
| Legend | Show legend (true/false) | `True` for multi-series |
| Tooltips | Hover data format | `"Region: %{x}<br>Sales: %{y:.1f}"` |
| Customization | Colours, annotations, layout | optional |

## Chart type reference

| Chart type | Best for | Trace | Code pattern |
|------------|----------|-------|--------------|
| Bar | Categorical comparisons | `go.Bar` | [Pattern](./references/chart-patterns.md#1-bar-chart) |
| Grouped Bar | Multi-category comparisons | `go.Bar` (multiple traces) | [Stacked bar](./references/chart-patterns.md#6-stacked-bar-chart) with `barmode='group'` |
| Stacked Bar | Part-to-whole by category | `go.Bar` with `barmode='stack'` | [Pattern](./references/chart-patterns.md#6-stacked-bar-chart) |
| Line | Trends over time | `go.Scatter` mode='lines+markers' | [Pattern](./references/chart-patterns.md#2-line-chart) |
| Bar + Line | Dual-axis comparison | `go.Bar` + `go.Scatter` | [Pattern](./references/chart-patterns.md#7-bar--line-combo) |
| Scatter | Correlation / distribution | `go.Scatter` mode='markers' | [Pattern](./references/chart-patterns.md#3-scatter-plot) |
| Heatmap | Matrix / density | `go.Heatmap` | [Pattern](./references/chart-patterns.md#4-heatmap) |
| Area | Cumulative trends | `go.Scatter` fill='tonexty' | [Pattern](./references/chart-patterns.md#5-area-chart) |
| Pie | Proportions (≤5 categories) | `go.Pie` | [Pattern](./references/chart-patterns.md#8-pie-chart) |
| Histogram | Distribution shape | `go.Histogram` | [Pattern](./references/chart-patterns.md#9-histogram) |
| Boxplot | Distribution + outliers | `go.Box` | [Pattern](./references/chart-patterns.md#10-boxplot) |
| Bubble | 3-variable relationship | `go.Scatter` with size param | [Pattern](./references/chart-patterns.md#11-bubble-chart) |
| Violin | Distribution density | `go.Violin` | [Pattern](./references/chart-patterns.md#12-violin-plot) |
| Funnel | Stage progression | `go.Funnel` | [Pattern](./references/chart-patterns.md#13-funnel-chart) |
| Waterfall | Incremental changes | `go.Waterfall` | [Pattern](./references/chart-patterns.md#14-waterfall-chart) |
| Sankey | Flow / migration | `go.Sankey` | [Pattern](./references/chart-patterns.md#15-sankey-diagram) |
| Treemap | Hierarchy | `go.Treemap` | [Pattern](./references/chart-patterns.md#16-treemap) |
| Sunburst | Nested hierarchy | `go.Sunburst` | [Pattern](./references/chart-patterns.md#17-sunburst) |
| Indicator | Single KPI | `go.Indicator` | [Pattern](./references/chart-patterns.md#18-indicator--kpi-tile) |
| Horizontal Bar | Ranked list | `go.Bar` orientation='h' | [Pattern](./references/chart-patterns.md#19-horizontal-bar-ranked) |
| Dumbbell | Before → after | `go.Scatter` + shapes | [Pattern](./references/chart-patterns.md#20-dumbbell-chart) |
| Radar | Multi-dimensional | `go.Scatterpolar` | [Pattern](./references/chart-patterns.md#21-radar--spider-chart) |
| Cohort Heatmap | Retention matrix | `go.Heatmap` (sequential scale) | [Pattern](./references/chart-patterns.md#22-cohort-retention-heatmap) |


## Styling rules

1. **plotly.express + colours**: When using `px`, MUST pass `color_discrete_sequence=chart_colours`. Do NOT let Plotly defaults override the palette.
2. **Horizontal bars / continuous x-axis**: Add `fig.update_xaxes(showgrid=True)` to restore the x-grid.
3. **Decimal formatting**: Format to 1 decimal place (`.1f`) unless the data is integer counts.
4. **Hover template**: Include x (if non-ordinal), y, and category. Example: `hovertemplate="Region: %{x}<br>Avg sales: %{y:.1f}<br><extra></extra>"`.
5. **String formatting in hover**: Avoid f-strings in `hovertemplate`. Use string concatenation: `"<b>" + series + "</b><br>Value: %{y:.1f}<extra></extra>"`.
6. **Colour overflow**: `chart_colours` has 7 colours. Past 7 categories colours repeat via `series_colours(n)`, which makes series ambiguous. Prefer fewer series: highlight the one or two that matter in colour and draw the rest in `COLOUR_MUTED`, or split into small multiples.
7. **Line charts**: ALWAYS sort by the x-axis column before plotting (Plotly connects points in order). With multiple series, sort by the series column first (`df.sort_values([series_col, x_col])`) so the legend order and series colours are the same on every run.
8. **Legend position**: Default is top-right. For area/stacked charts, use a horizontal legend above: `legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)`.
9. **Light colours**: Several palette colours (`#FFB651`, `#DAA5AC`, `#61BEA4`) are under 3:1 contrast on white. Use them for filled areas and bars, not thin lines or text.
10. **Created-at annotation**: Call `add_created_at_annotation(fig)` on every chart before `fig.show()`. Ensure the creation date is fully visible and does not overlap axis labels or titles. Adjust offset_px and bottom_margin_px when needed.

## Axes

- The x-axis grid is **off by default**. Re-enable it with `fig.update_xaxes(showgrid=True)` for horizontal bar charts or when the x-axis is continuous.
- The y-axis grid is always on.

## Saving charts

- Interactive: `fig.write_html("chart.html", include_plotlyjs=True, full_html=True)` produces a self-contained file.
- Static image: `fig.write_image("chart.png")` (requires `pip install kaleido`).

## Customising

Edit the `STYLE SETTINGS` block in the preamble: swap `chart_colours` for any list of hex colours, change `FONT_FAMILY`, or change the default size. All patterns in [chart-patterns.md](./references/chart-patterns.md) read from those names, so a change there restyles every chart.
